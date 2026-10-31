type PlaybackControlsProps = {
  currentIndex: number;
  totalSteps: number;
  isPlaying: boolean;
  onPlay: () => void;
  onPause: () => void;
  onStepBack: () => void;
  onStepForward: () => void;
};

function PlaybackControls({
  currentIndex,
  totalSteps,
  isPlaying,
  onPlay,
  onPause,
  onStepBack,
  onStepForward,
}: PlaybackControlsProps) {
  const hasSteps = totalSteps > 0;

  return (
    <div className="playback-controls">
      <div className="playback-status">
        {hasSteps ? `Step ${currentIndex + 1} of ${totalSteps}` : 'No steps'}
      </div>

      <div className="playback-buttons">
        <button type="button" onClick={onStepBack} disabled={!hasSteps || currentIndex <= 0}>
          Step Back
        </button>
        <button type="button" onClick={onPlay} disabled={!hasSteps || isPlaying}>
          Play
        </button>
        <button type="button" onClick={onPause} disabled={!isPlaying}>
          Pause
        </button>
        <button
          type="button"
          onClick={onStepForward}
          disabled={!hasSteps || currentIndex >= totalSteps - 1}
        >
          Step Forward
        </button>
      </div>
    </div>
  );
}

export default PlaybackControls;
