// src/components/analytics/utils.js

export function formatPercentage(value) {
  return `${value}%`;
}

export function formatReportDate(date) {
  return new Date(date).toLocaleDateString();
}

export function getTotalIncidents(data) {
  return data.reduce((sum, item) => sum + item.value, 0);
}

export function calculateAverageConfidence(cameras) {
  if (!cameras.length) return 0;

  const total = cameras.reduce(
    (sum, camera) => sum + camera.confidence,
    0
  );

  return Math.round(total / cameras.length);
}