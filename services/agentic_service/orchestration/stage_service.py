from typing import Any, Dict, Optional

from orchestration.approval_manager import ApprovalManager
from orchestration.error_manager import ErrorManager
from orchestration.run_manager import RunManager
from orchestration.version_manager import VersionManager
from agents.architect_agent import agent
from states.artifact_registry import ArtifactRegistry
from states.system_state import WorkflowState


class StageService:
    """
    Main orchestration service.

    This service controls:
    - run creation
    - stage generation
    - approval
    - rejection
    - revision
    - dependency checks

    Important:
    Agents are imported lazily inside methods.
    This prevents unrelated agent dependencies from breaking the whole API.
    """

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        self.run_manager = RunManager(output_dir=output_dir)
        self.approval_manager = ApprovalManager(output_dir=output_dir)
        self.error_manager = ErrorManager(output_dir=output_dir)

    def create_run(self, project_name: Optional[str] = None, run_id: Optional[str] = None) -> WorkflowState:
        """
        Creates a new workflow run.
        """

        return self.run_manager.create_run(
            project_name=project_name,
            run_id=run_id,
        )

    def get_status(self, run_id: str) -> dict:
        """
        Returns workflow state and approval state.
        """

        state = self.run_manager.load_state(run_id)
        approvals = self.approval_manager.get_approval_state(run_id)

        return {
            "state": state.model_dump(),
            "approvals": approvals,
        }

    def get_artifacts(self, run_id: str) -> dict:
        """
        Returns all artifacts registered for a run.
        """

        state = self.run_manager.load_state(run_id)

        return {
            "run_id": run_id,
            "artifacts": [artifact.model_dump() for artifact in state.artifacts],
        }
    
    def ingest_domain_knowledge(self, payload: Dict[str, Any]) -> dict:
        """
        Ingests the E-commerce domain knowledge text file into a vector store.

        This method prepares the RAG knowledge base used by the Domain Agent.

        Supported vector stores:
        - faiss
        - chroma

        Example payload:
        {
          "file_path": "knowledge/ecommerce_domain_knowledge.txt",
          "vector_store_type": "faiss"
        }
        """

        # Lazy import:
        # We import DomainAgent only when this method is called.
        # This keeps API startup lightweight and avoids loading unnecessary
        # agent dependencies before they are needed.
        from agents.domain_agent.agent import DomainAgent
        from tools.llm.provider import OllamaProvider

        file_path = payload.get("file_path", "knowledge/ecommerce_domain_knowledge.txt")
        vector_store_type = payload.get("vector_store_type", "faiss")

        agent = DomainAgent(llm_provider=OllamaProvider())

        result = agent.ingest_domain_knowledge(
            file_path=file_path,
            vector_store_type=vector_store_type,
        )

        return {
            "message": "Domain knowledge ingested successfully.",
            "result": result,
        }

    async def generate_stage(
        self,
        run_id: str,
        stage: str,
        payload: Dict[str, Any],
    ) -> dict:
        """
        Generates a stage output.

        Supported now:
        - requirements
        - domain

        Later we will extend:
        - architecture
        - uiux
        - code
        - tests
        - security
        - export
        """

        normalized_stage = stage.lower().strip()

        try:
            if normalized_stage == "requirements":
                return await self._generate_requirements(run_id, payload)

            if normalized_stage == "domain":
                return await self._generate_domain(run_id, payload)

            if normalized_stage == "architecture":
                return await self._generate_architecture(run_id, payload)

            raise ValueError(
                f"Unsupported stage: {stage}. Currently supported: requirements, domain, architecture."
            )

        except Exception as error:
            # Store error in workflow error log.
            workflow_error = self.error_manager.append_error(
                run_id=run_id,
                stage=normalized_stage,
                error_type=type(error).__name__,
                message=str(error),
            )

            # Also update workflow_state.json if possible.
            try:
                state = self.run_manager.load_state(run_id)
                state.errors.append(workflow_error)
                state.current_stage = "WORKFLOW_FAILED"
                state.next_action = f"Fix error in {normalized_stage} stage and retry."
                self.run_manager.save_state(state)
            except Exception:
                # If state loading itself fails, return original error only.
                pass

            raise error

    async def _generate_requirements(
        self,
        run_id: str,
        payload: Dict[str, Any],
    ) -> dict:
        """
        Calls Requirement Agent and registers SRS artifacts.

        Expected payload:
        {
          "intake": {...}
        }
        """

        # Lazy imports: only load Requirement Agent when this stage runs.
        from agents.requirement_agent.agent import RequirementAgent
        from tools.llm.provider import OllamaProvider

        state = self.run_manager.load_state(run_id)

        intake = payload.get("intake", payload)

        if not intake:
            raise ValueError("Missing intake data for requirements generation.")

        current_version = state.latest_versions.get("requirements")
        new_version = VersionManager.next_version(current_version)

        agent = RequirementAgent(llm_provider=OllamaProvider())

        result = await agent.generate_srs(
            intake_data=intake,
            run_id=run_id,
            version=new_version,
        )

        # Update project name if available.
        state.project_name = result.get("srs", {}).get("project_name", state.project_name)

        state.latest_versions["requirements"] = new_version
        state.current_stage = "SRS_PENDING_APPROVAL"
        state.pending_approval_stage = "requirements"
        state.next_action = f"Review and approve or reject SRS_{new_version}."

        state.messages.append(f"Requirement Agent generated SRS_{new_version}.")

        ArtifactRegistry.add_artifact(
            state=state,
            stage="requirements",
            version=new_version,
            artifact_type="json",
            path=result["json_path"],
            status="pending_approval",
        )

        ArtifactRegistry.add_artifact(
            state=state,
            stage="requirements",
            version=new_version,
            artifact_type="markdown",
            path=result["markdown_path"],
            status="pending_approval",
        )

        self.approval_manager.set_pending(
            run_id=run_id,
            stage="requirements",
            version=new_version,
            comment="SRS generated and waiting for human approval.",
        )

        self.run_manager.save_state(state)

        return {
            "message": "Requirement stage generated successfully.",
            "state": state.model_dump(),
            "result": result,
        }

    async def _generate_domain(
        self,
        run_id: str,
        payload: Dict[str, Any],
    ) -> dict:
        """
        Calls Domain Agent and registers DomainPack artifacts.

        Expected payload:
        {
          "srs_version": "v1",
          "domain_version": "v1", optional
          "vector_store_type": "faiss",
          "top_k": 6
        }
        """

        # Lazy imports: only load Domain Agent when this stage runs.
        from agents.domain_agent.agent import DomainAgent
        from tools.llm.provider import OllamaProvider

        state = self.run_manager.load_state(run_id)

        srs_version = payload.get("srs_version") or state.latest_versions.get("requirements")

        if not srs_version:
            raise ValueError("No SRS version found. Generate requirements first.")

        if not self.approval_manager.is_approved(run_id, "requirements", srs_version):
            raise ValueError(
                f"Cannot generate DomainPack. Requirements {srs_version} is not approved."
            )

        current_domain_version = state.latest_versions.get("domain")
        new_domain_version = VersionManager.next_version(current_domain_version)

        vector_store_type = payload.get("vector_store_type", "faiss")
        top_k = payload.get("top_k", 6)

        agent = DomainAgent(llm_provider=OllamaProvider())

        result = await agent.generate_domain_pack(
            run_id=run_id,
            srs_version=srs_version,
            domain_version=new_domain_version,
            vector_store_type=vector_store_type,
            top_k=top_k,
        )

        state.latest_versions["domain"] = new_domain_version
        state.current_stage = "DOMAIN_PENDING_APPROVAL"
        state.pending_approval_stage = "domain"
        state.next_action = f"Review and approve or reject DomainPack_{new_domain_version}."

        state.messages.append(f"Domain Agent generated DomainPack_{new_domain_version}.")

        ArtifactRegistry.add_artifact(
            state=state,
            stage="domain",
            version=new_domain_version,
            artifact_type="json",
            path=result["json_path"],
            status="pending_approval",
        )

        ArtifactRegistry.add_artifact(
            state=state,
            stage="domain",
            version=new_domain_version,
            artifact_type="markdown",
            path=result["markdown_path"],
            status="pending_approval",
        )

        self.approval_manager.set_pending(
            run_id=run_id,
            stage="domain",
            version=new_domain_version,
            comment="DomainPack generated and waiting for human approval.",
        )

        self.run_manager.save_state(state)

        return {
            "message": "Domain stage generated successfully.",
            "state": state.model_dump(),
            "result": result,
        }

    async def _generate_architecture(
        self,
        run_id: str,
        payload: Dict[str, Any],
    ) -> dict:
        """
        Calls Architect Agent and registers Architecture/SDS/API artifacts.

        Dependency rule:
        Architecture cannot run unless:
        1. Requirements are approved
        2. DomainPack is approved

        Expected payload:
        {
          "srs_version": "v1",
          "domain_version": "v1"
        }

        The architecture_version is generated automatically by the orchestrator.
        """

        # Lazy imports:
        # The Architect Agent is imported only when this stage is executed.
        # This keeps Uvicorn startup stable even if Architect dependencies
        # are not ready during Requirement/Domain development.
        from agents.architect_agent.agent import ArchitectAgent
        from tools.llm.provider import OllamaProvider
        from orchestration.agent_adapters import call_architect_agent

        state = self.run_manager.load_state(run_id)

        srs_version = payload.get("srs_version") or state.latest_versions.get("requirements")
        domain_version = payload.get("domain_version") or state.latest_versions.get("domain")

        if not srs_version:
            raise ValueError("No SRS version found. Generate and approve requirements first.")

        if not domain_version:
            raise ValueError("No DomainPack version found. Generate and approve domain stage first.")

        if not self.approval_manager.is_approved(run_id, "requirements", srs_version):
            raise ValueError(
                f"Cannot generate architecture. Requirements {srs_version} is not approved."
            )

        if not self.approval_manager.is_approved(run_id, "domain", domain_version):
            raise ValueError(
                f"Cannot generate architecture. DomainPack {domain_version} is not approved."
            )

        current_architecture_version = state.latest_versions.get("architecture")
        new_architecture_version = VersionManager.next_version(current_architecture_version)

        try:
            agent = ArchitectAgent(llm_provider=OllamaProvider())
        except TypeError:
            agent = ArchitectAgent()

        result = await call_architect_agent(
            agent=agent,
            run_id=run_id,
            srs_version=srs_version,
            domain_version=domain_version,
            architecture_version=new_architecture_version,
        )

        if not isinstance(result, dict):
            raise ValueError(
                "Architect Agent returned invalid result. Expected a dictionary with artifact paths."
            )

        state.latest_versions["architecture"] = new_architecture_version
        state.current_stage = "ARCHITECTURE_PENDING_APPROVAL"
        state.pending_approval_stage = "architecture"
        state.next_action = (
            f"Review and approve or reject Architecture/SDS {new_architecture_version}."
        )

        state.messages.append(
            f"Architect Agent generated architecture artifacts for {new_architecture_version}."
        )

        # Register common architecture artifact paths if the Architect Agent returns them.
        # This supports different Architect Agent output designs.
        artifact_key_map = {
            "json_path": "json",
            "markdown_path": "markdown",
            "sds_json_path": "sds_json",
            "sds_markdown_path": "sds_markdown",
            "openapi_json_path": "openapi_json",
            "openapi_yaml_path": "openapi_yaml",
            "db_pack_path": "db_pack",
            "diagram_manifest_path": "diagram_manifest",
        }

        registered_count = 0

        for key, artifact_type in artifact_key_map.items():
            path = result.get(key)

            if path:
                ArtifactRegistry.add_artifact(
                    state=state,
                    stage="architecture",
                    version=new_architecture_version,
                    artifact_type=artifact_type,
                    path=path,
                    status="pending_approval",
                )

                registered_count += 1

        # Some Architect Agents return a list of artifacts.
        # Example:
        # "artifacts": [
        #   {"type": "openapi_yaml", "path": "..."},
        #   {"type": "class_diagram", "path": "..."}
        # ]
        for artifact in result.get("artifacts", []):
            artifact_type = artifact.get("type", "architecture_artifact")
            path = artifact.get("path")

            if path:
                ArtifactRegistry.add_artifact(
                    state=state,
                    stage="architecture",
                    version=new_architecture_version,
                    artifact_type=artifact_type,
                    path=path,
                    status="pending_approval",
                )

                registered_count += 1

        if registered_count == 0:
            raise ValueError(
                "Architect Agent completed but returned no recognizable artifact paths. "
                "Expected keys like json_path, markdown_path, openapi_yaml_path, or artifacts[]."
            )

        self.approval_manager.set_pending(
            run_id=run_id,
            stage="architecture",
            version=new_architecture_version,
            comment="Architecture artifacts generated and waiting for human approval.",
        )

        self.run_manager.save_state(state)

        return {
            "message": "Architecture stage generated successfully.",
            "state": state.model_dump(),
            "result": result,
        }

    async def revise_stage(
        self,
        run_id: str,
        stage: str,
        payload: Dict[str, Any],
    ) -> dict:
        """
        Revises a stage artifact.

        Supported now:
        - requirements revision using RequirementAgent.revise_srs

        Domain revision will be handled later with a dedicated DomainAgent revision method.
        For now, rejected domain can be regenerated using generate_stage.
        """

        normalized_stage = stage.lower().strip()

        if normalized_stage != "requirements":
            raise ValueError(
                "Revision is currently implemented only for requirements. "
                "For domain, reject the current version and generate a new DomainPack."
            )

        from agents.requirement_agent.agent import RequirementAgent
        from tools.llm.provider import OllamaProvider

        state = self.run_manager.load_state(run_id)

        current_version = payload.get("current_version") or state.latest_versions.get("requirements")

        if not current_version:
            raise ValueError("No current SRS version found to revise.")

        change_request = payload.get("change_request")

        if not change_request:
            raise ValueError("Missing change_request for SRS revision.")

        new_version = VersionManager.next_version(current_version)

        agent = RequirementAgent(llm_provider=OllamaProvider())

        result = await agent.revise_srs(
            run_id=run_id,
            current_version=current_version,
            new_version=new_version,
            change_request=change_request,
        )

        state.latest_versions["requirements"] = new_version
        state.current_stage = "SRS_PENDING_APPROVAL"
        state.pending_approval_stage = "requirements"
        state.next_action = f"Review and approve or reject revised SRS_{new_version}."

        state.messages.append(
            f"Requirement Agent revised SRS from {current_version} to {new_version}."
        )

        ArtifactRegistry.add_artifact(
            state=state,
            stage="requirements",
            version=new_version,
            artifact_type="json",
            path=result["json_path"],
            status="pending_approval",
        )

        ArtifactRegistry.add_artifact(
            state=state,
            stage="requirements",
            version=new_version,
            artifact_type="markdown",
            path=result["markdown_path"],
            status="pending_approval",
        )

        self.approval_manager.set_pending(
            run_id=run_id,
            stage="requirements",
            version=new_version,
            comment=f"Revised because: {change_request}",
        )

        self.run_manager.save_state(state)

        return {
            "message": "Requirement stage revised successfully.",
            "state": state.model_dump(),
            "result": result,
        }

    def approve_stage(
        self,
        run_id: str,
        stage: str,
        payload: Dict[str, Any],
    ) -> dict:
        """
        Approves a stage/version.

        Expected payload:
        {
          "version": "v1",
          "comment": "Approved"
        }
        """

        normalized_stage = stage.lower().strip()

        state = self.run_manager.load_state(run_id)

        version = payload.get("version") or state.latest_versions.get(normalized_stage)

        if not version:
            raise ValueError(f"No version found for stage: {normalized_stage}")

        comment = payload.get("comment", "Approved by human user.")

        self.approval_manager.approve(
            run_id=run_id,
            stage=normalized_stage,
            version=version,
            comment=comment,
        )

        ArtifactRegistry.update_artifact_status(
            state=state,
            stage=normalized_stage,
            version=version,
            status="approved",
        )

        if normalized_stage not in state.approved_stages:
            state.approved_stages.append(normalized_stage)

        state.pending_approval_stage = None

        if normalized_stage == "requirements":
            state.current_stage = "SRS_APPROVED"
            state.next_action = "Generate DomainPack using the Domain Agent."

        elif normalized_stage == "domain":
            state.current_stage = "DOMAIN_APPROVED"
            state.next_action = "Generate architecture using the Architect Agent."

        elif normalized_stage == "architecture":
            state.current_stage = "ARCHITECTURE_APPROVED"
            state.next_action = "Next stage is UI/UX Agent."

        else:
            state.current_stage = f"{normalized_stage.upper()}_APPROVED"
            state.next_action = "Continue to the next stage."

        state.messages.append(f"{normalized_stage} {version} approved.")

        self.run_manager.save_state(state)

        return {
            "message": f"{normalized_stage} {version} approved successfully.",
            "state": state.model_dump(),
            "approvals": self.approval_manager.get_approval_state(run_id),
        }

    def reject_stage(
        self,
        run_id: str,
        stage: str,
        payload: Dict[str, Any],
    ) -> dict:
        """
        Rejects a stage/version.

        Expected payload:
        {
          "version": "v1",
          "comment": "Add search requirement"
        }
        """

        normalized_stage = stage.lower().strip()

        state = self.run_manager.load_state(run_id)

        version = payload.get("version") or state.latest_versions.get(normalized_stage)

        if not version:
            raise ValueError(f"No version found for stage: {normalized_stage}")

        comment = payload.get("comment", "Rejected by human user.")

        self.approval_manager.reject(
            run_id=run_id,
            stage=normalized_stage,
            version=version,
            comment=comment,
        )

        ArtifactRegistry.update_artifact_status(
            state=state,
            stage=normalized_stage,
            version=version,
            status="rejected",
        )

        state.pending_approval_stage = None

        if normalized_stage == "requirements":
            state.current_stage = "SRS_REJECTED"
            state.next_action = "Revise the SRS using /runs/{run_id}/stages/requirements/revise."

        elif normalized_stage == "domain":
            state.current_stage = "DOMAIN_REJECTED"
            state.next_action = "Generate a new DomainPack version after fixing the issue."

        elif normalized_stage == "architecture":
            state.current_stage = "ARCHITECTURE_REJECTED"
            state.next_action = "Generate a new architecture version after fixing the issue."

        else:
            state.current_stage = f"{normalized_stage.upper()}_REJECTED"
            state.next_action = "Revise or regenerate this stage."

        state.messages.append(f"{normalized_stage} {version} rejected. Reason: {comment}")

        self.run_manager.save_state(state)

        return {
            "message": f"{normalized_stage} {version} rejected.",
            "state": state.model_dump(),
            "approvals": self.approval_manager.get_approval_state(run_id),
        }
