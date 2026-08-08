import { useEffect, useRef, useState } from "react";

export default function useCounter(
  endValue,
  {
    startValue = 0,
    duration = 1200,
    decimals = 0,
  } = {}
) {
  const [count, setCount] = useState(startValue);
  const frameRef = useRef();

  useEffect(() => {
    let startTime = null;

    const animate = (timestamp) => {
      if (!startTime) {
        startTime = timestamp;
      }

      const progress = Math.min(
        (timestamp - startTime) / duration,
        1
      );

      const value =
        startValue + (endValue - startValue) * progress;

      setCount(Number(value.toFixed(decimals)));

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(animate);
      }
    };

    frameRef.current = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(frameRef.current);
    };
  }, [startValue, endValue, duration, decimals]);

  return count;
}