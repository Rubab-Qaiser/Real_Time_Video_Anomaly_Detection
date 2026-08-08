import {
  Camera,
  Play,
  Pause,
  RotateCcw,
  Download,
  Video,
} from "lucide-react";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function CameraControls() {
  return (
    <Card className="border-slate-800 bg-slate-900 p-4">

      <div className="flex flex-wrap items-center justify-between gap-4">

        {/* Left */}

        <div className="flex flex-wrap gap-2">

          <Button>

            <Play className="mr-2 h-4 w-4" />

            Start

          </Button>

          <Button variant="secondary">

            <Pause className="mr-2 h-4 w-4" />

            Pause

          </Button>

          <Button variant="outline">

            <RotateCcw className="mr-2 h-4 w-4" />

            Restart

          </Button>

        </div>

        {/* Right */}

        <div className="flex flex-wrap gap-2">

          <Button variant="outline">

            <Camera className="mr-2 h-4 w-4" />

            Snapshot

          </Button>

          <Button variant="outline">

            <Video className="mr-2 h-4 w-4" />

            Record

          </Button>

          <Button variant="outline">

            <Download className="mr-2 h-4 w-4" />

            Export

          </Button>

        </div>

      </div>

    </Card>
  );
}