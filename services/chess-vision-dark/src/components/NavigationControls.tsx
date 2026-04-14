import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import {
  ChevronsLeft,
  ChevronLeft,
  ChevronRight,
  ChevronsRight,
  Play,
  Pause,
  ArrowUpDown,
} from 'lucide-react';

interface NavigationControlsProps {
  onFirst: () => void;
  onPrev: () => void;
  onNext: () => void;
  onLast: () => void;
  onFlip: () => void;
  isPlaying: boolean;
  onTogglePlay: () => void;
  speed: number;
  onSpeedChange: (speed: number) => void;
  canPrev: boolean;
  canNext: boolean;
}

export function NavigationControls({
  onFirst, onPrev, onNext, onLast, onFlip,
  isPlaying, onTogglePlay,
  speed, onSpeedChange,
  canPrev, canNext,
}: NavigationControlsProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-center gap-1 bg-muted/50 rounded-xl p-1.5">
        <Button variant="ghost" size="icon" onClick={onFirst} disabled={!canPrev} title="First move (Home)" className="h-12 w-12 rounded-lg hover:bg-background/80 disabled:opacity-30">
          <ChevronsLeft className="h-6 w-6" />
        </Button>
        <Button variant="ghost" size="icon" onClick={onPrev} disabled={!canPrev} title="Previous move (←)" className="h-12 w-12 rounded-lg hover:bg-background/80 disabled:opacity-30">
          <ChevronLeft className="h-6 w-6" />
        </Button>
        <Button
          variant={isPlaying ? 'default' : 'ghost'}
          size="icon"
          onClick={onTogglePlay}
          title="Auto-play (Space)"
          className="h-12 w-12 rounded-lg"
        >
          {isPlaying ? <Pause className="h-6 w-6" /> : <Play className="h-6 w-6" />}
        </Button>
        <Button variant="ghost" size="icon" onClick={onNext} disabled={!canNext} title="Next move (→)" className="h-12 w-12 rounded-lg hover:bg-background/80 disabled:opacity-30">
          <ChevronRight className="h-6 w-6" />
        </Button>
        <Button variant="ghost" size="icon" onClick={onLast} disabled={!canNext} title="Last move (End)" className="h-12 w-12 rounded-lg hover:bg-background/80 disabled:opacity-30">
          <ChevronsRight className="h-6 w-6" />
        </Button>
        <div className="w-px h-6 bg-border/60 mx-2" />
        <Button variant="ghost" size="icon" onClick={onFlip} title="Flip board (F)" className="h-12 w-12 rounded-lg hover:bg-background/80">
          <ArrowUpDown className="h-6 w-6" />
        </Button>
      </div>
      <div className="flex items-center gap-2 px-1">
        <span className="text-xs text-muted-foreground whitespace-nowrap font-medium">Speed</span>
        <Slider
          min={200}
          max={3000}
          step={100}
          value={[speed]}
          onValueChange={([v]) => onSpeedChange(v)}
          className="flex-1"
        />
        <span className="text-xs text-muted-foreground w-10 text-right font-mono">{(speed / 1000).toFixed(1)}s</span>
      </div>
    </div>
  );
}
