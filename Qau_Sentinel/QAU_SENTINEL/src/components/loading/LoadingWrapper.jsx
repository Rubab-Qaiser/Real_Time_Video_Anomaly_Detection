export default function LoadingWrapper({
  loading,
  skeleton,
  children,
}) {
  if (loading) {
    return skeleton;
  }

  return children;
}