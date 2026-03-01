export const Header = () => {
  return (
    <header className="border-b border-primary-700 bg-primary-800/50 backdrop-blur-sm">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚽</span>
          <div>
            <h1 className="text-lg font-bold text-white">UCL Fantasy Scout</h1>
            <p className="text-xs text-primary-300">
              AI-Powered Squad Analysis
            </p>
          </div>
        </div>
        <span className="rounded-full bg-ucl-gold/20 px-3 py-1 text-xs font-medium text-ucl-gold">
          v1.0
        </span>
      </div>
    </header>
  );
};
