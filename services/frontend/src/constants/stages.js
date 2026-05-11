import {
  ClipboardList,
  BookOpenText,
  Network,
  Palette,
  Code2,
  ShieldCheck,
  FlaskConical
} from "lucide-react";

export const PIPELINE_STAGES = [
  {
    id: "requirements",
    title: "Requirement Agent",
    shortTitle: "Requirements",
    description: "Generate and revise SRS artifacts with FR, NFR, AC, and use cases.",
    icon: ClipboardList
  },
  {
    id: "domain",
    title: "Domain Agent",
    shortTitle: "Domain",
    description: "Generate e-commerce domain pack, workflows, and business rules.",
    icon: BookOpenText
  },
  {
    id: "architect",
    title: "Architect Agent",
    shortTitle: "Architecture",
    description: "Generate SDS, API contracts, UML diagrams, and database design.",
    icon: Network
  },
  {
    id: "uiux",
    title: "UI/UX Agent",
    shortTitle: "UI/UX",
    description: "Generate user flows, wireframes, and design pack.",
    icon: Palette
  },
  {
    id: "coder",
    title: "Coder Agent",
    shortTitle: "Coder",
    description: "Generate application code, database files, and DevOps artifacts.",
    icon: Code2
  },
  {
    id: "security",
    title: "Security Agent",
    shortTitle: "Security",
    description: "Run security analysis and produce vulnerability reports.",
    icon: ShieldCheck
  },
  {
    id: "qa",
    title: "QA Agent",
    shortTitle: "QA",
    description: "Generate and run test suites with QA reports.",
    icon: FlaskConical
  }
];

export function getStageById(stageId) {
  return PIPELINE_STAGES.find((stage) => stage.id === stageId) || PIPELINE_STAGES[0];
}