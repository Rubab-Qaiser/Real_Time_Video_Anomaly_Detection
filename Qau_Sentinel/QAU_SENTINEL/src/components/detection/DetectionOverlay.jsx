import DetectionBox from "./DetectionBox";

export default function DetectionOverlay({
  detections = [],
}) {
  if (!detections.length) return null;

  return (
    <div
      className="
        absolute
        inset-0
        z-20
        overflow-hidden
        pointer-events-none
      "
    >
      {detections.map((detection) => (
        <DetectionBox
          key={detection.id}
          detection={detection}
        />
      ))}
    </div>
  );
}