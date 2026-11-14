export default function HealthStatus({ health, error }) {
  if (error) {
    return <p className="status error">Backend unavailable: {error}</p>;
  }
  if (!health) {
    return <p className="status">Checking backend connectivity...</p>;
  }
  return (
    <p className="status success">
      API status: {health.status} ({health.mode} mode)
    </p>
  );
}
