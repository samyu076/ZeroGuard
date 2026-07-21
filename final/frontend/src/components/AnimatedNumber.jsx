import React, { useEffect, useState, useRef } from 'react';

export default function AnimatedNumber({ value = 0.0, decimals = 1, suffix = '' }) {
  const [displayValue, setDisplayValue] = useState(value);
  const prevValueRef = useRef(value);

  useEffect(() => {
    const startVal = prevValueRef.current;
    const endVal = value;
    if (startVal === endVal) {
      setDisplayValue(endVal);
      return;
    }

    const duration = 500; // 500ms ease-out
    const startTime = performance.now();

    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1.0);

      // Ease-out cubic formula: 1 - pow(1 - progress, 3)
      const easeOutProgress = 1 - Math.pow(1 - progress, 3);
      const current = startVal + (endVal - startVal) * easeOutProgress;

      setDisplayValue(current);

      if (progress < 1.0) {
        requestAnimationFrame(animate);
      } else {
        prevValueRef.current = endVal;
      }
    };

    requestAnimationFrame(animate);
  }, [value]);

  return (
    <span className="font-mono-tech leading-[1.2]">
      {displayValue.toFixed(decimals)}{suffix}
    </span>
  );
}
