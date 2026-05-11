export default function TextInput({
    label,
    name,
    value,
    onChange,
    placeholder,
    type = "text",
    textarea = false,
    rows = 4,
    required = false,
    helper,
  }) {
    return (
      <div className="form-field">
        <label htmlFor={name}>
          {label}
          {required && <span className="required">*</span>}
        </label>
  
        {textarea ? (
          <textarea
            id={name}
            name={name}
            rows={rows}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
          />
        ) : (
          <input
            id={name}
            name={name}
            type={type}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
          />
        )}
  
        {helper && <small>{helper}</small>}
      </div>
    );
  }