import useCounter from "@/hooks/useCounter";

export default function AnimatedCounter({
  value,
  start = 0,
  duration = 1200,
  decimals = 0,
  className = "",
}) {
  const count = useCounter(value, {
    startValue: start,
    duration,
    decimals,
  });

  return (
    <span className={className}>
      {count}
    </span>
  );
}