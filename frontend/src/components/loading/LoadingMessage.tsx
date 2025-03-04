import React, { useState, useEffect } from 'react';

export const LoadingMessage: React.FC = () => {
  const maxLines = 6; // Number of lines
  const maxWidth = 50; // Max possible width per line

  // Generate a random length for each line
  const generateRandomLengths = () =>
    Array.from({ length: maxLines }).map(() => Math.floor(Math.random() * maxWidth * 0.8) + 10);

  // Generate random speeds for each line
  const generateRandomSpeeds = () =>
    Array.from({ length: maxLines }).map(() => Math.floor(Math.random() * 100) + 80); // Varies between 80ms-180ms

  // State for tracking each line's progress
  const [lineProgress, setLineProgress] = useState(Array(maxLines).fill(1));
  const [lineMaxWidths, setLineMaxWidths] = useState(generateRandomLengths());
  const [lineSpeeds, setLineSpeeds] = useState(generateRandomSpeeds());

  useEffect(() => {
    const intervals = lineProgress.map((_, i) =>
      setInterval(() => {
        setLineProgress((prev) =>
          prev.map((val, index) =>
            index === i
              ? val < lineMaxWidths[index]
                ? val + 1 // Expand line
                : 1 // Reset independently
              : val
          )
        );
      }, lineSpeeds[i]) // Each line has its own speed
    );

    return () => intervals.forEach(clearInterval);
  }, [lineMaxWidths, lineSpeeds]);

  return (
    <div className="font-mono text-xs leading-relaxed p-2">
      {lineProgress.map((progress, i) => (
        <div key={i} className="mb-1"> {/* Adds spacing between lines */}
          {':'.repeat(progress)} {/* Always starts with ":" and grows */}
        </div>
      ))}
    </div>
  );
};
