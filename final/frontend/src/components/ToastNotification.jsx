import React, { useEffect } from 'react';
import { CheckCircle, AlertTriangle, X } from 'lucide-react';

export default function ToastNotification({ toast, onClose }) {
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => {
      onClose();
    }, 3000);
    return () => clearTimeout(timer);
  }, [toast, onClose]);

  if (!toast) return null;

  const isError = toast.type === 'error';

  return (
    <div className="fixed top-[70px] right-[24px] z-50 animate-toast">
      <div
        className={`p-[16px] rounded-[6px] border shadow-xl flex items-center gap-[12px] min-w-[300px] max-w-md font-mono-tech text-[12px] ${
          isError
            ? 'bg-[#F85149]/15 border-[#F85149]/50 text-[#F85149]'
            : 'bg-[#161B22] border-[#58A6FF]/60 text-[#E6EDF3]'
        }`}
      >
        {isError ? (
          <AlertTriangle className="w-[18px] h-[18px] text-[#F85149] shrink-0" strokeWidth={1.5} />
        ) : (
          <CheckCircle className="w-[18px] h-[18px] text-[#58A6FF] shrink-0" strokeWidth={1.5} />
        )}
        <div className="flex-1 font-sans text-[12px]">
          <span className="font-bold block font-mono-tech uppercase text-[11px] text-[#8B949E]">
            {toast.title || 'SYSTEM NOTIFICATION'}
          </span>
          <span>{toast.message}</span>
        </div>
        <button
          onClick={onClose}
          className="text-[#8B949E] hover:text-[#E6EDF3] p-[2px]"
        >
          <X className="w-[14px] h-[14px]" strokeWidth={1.5} />
        </button>
      </div>
    </div>
  );
}
