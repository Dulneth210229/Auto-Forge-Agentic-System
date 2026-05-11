import Select from "../ui/Select.jsx";

export default function VersionSelector({
  label = "Version",
  value,
  onChange,
  versions = ["v1", "v2", "v3", "v4", "v5"]
}) {
  return (
    <Select label={label} value={value} onChange={(event) => onChange(event.target.value)}>
      {versions.map((version) => (
        <option key={version} value={version}>
          {version}
        </option>
      ))}
    </Select>
  );
}
