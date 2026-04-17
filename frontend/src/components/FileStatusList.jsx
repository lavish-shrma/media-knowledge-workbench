export default function FileStatusList({ files }) {
  return (
    <section className="panel">
      <h2>Uploaded Files</h2>
      {files.length === 0 ? <p>No files uploaded yet.</p> : null}
      {files.length > 0 ? (
        <ul className="file-list">
          {files.map((item) => (
            <li key={item.id}>
              <strong>{item.original_name}</strong>
              <span>{item.media_kind}</span>
              <span>{item.status}</span>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
