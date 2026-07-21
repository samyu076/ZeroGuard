import React, { useState, useRef } from 'react';
import { Upload, FileText, Search, CheckCircle2, AlertCircle, Loader } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

export default function RagUploaderPanel({ onTriggerToast }) {
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [standardName, setStandardName] = useState('');
  const [query, setQuery] = useState('');
  const [queryResults, setQueryResults] = useState(null);
  const [isQuerying, setIsQuerying] = useState(false);
  const fileInputRef = useRef(null);

  const fetchDocs = async () => {
    try {
      const res = await fetch(`${API_BASE}/compliance/uploaded-standards`);
      if (!res.ok) return;
      const data = await res.json();
      setUploadedDocs(data.documents || []);
    } catch (e) {}
  };

  const handleUpload = async (file) => {
    if (!file) return;
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('standard_name', standardName || file.name);

      const res = await fetch(`${API_BASE}/compliance/upload-standard`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();

      if (data.status === 'DOCUMENT_INGESTED') {
        fetchDocs();
        if (onTriggerToast) {
          onTriggerToast({
            title: 'DOCUMENT INGESTED',
            message: `${data.filename} — ${data.total_chunks} chunks vectorised into RAG engine.`
          });
        }
        setStandardName('');
      }
    } catch (e) {
      if (onTriggerToast) {
        onTriggerToast({ title: 'UPLOAD ERROR', message: e.message, type: 'error' });
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleUpload(file);
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setIsQuerying(true);
    setQueryResults(null);
    try {
      const formData = new FormData();
      formData.append('query', query);
      formData.append('top_k', '3');

      const res = await fetch(`${API_BASE}/compliance/rag-query`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setQueryResults(data);
    } catch (e) {
      setQueryResults({ results: [], message: `Query error: ${e.message}` });
    } finally {
      setIsQuerying(false);
    }
  };

  return (
    <div className="space-y-[20px]">
      {/* Upload Zone */}
      <div className="zg-card">
        <div className="flex items-center gap-[8px] mb-[16px] border-b border-[#21262D] pb-[16px]">
          <Upload className="w-[18px] h-[18px] text-[#58A6FF]" strokeWidth={1.5} />
          <h4 className="text-[13px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            DYNAMIC STATUTORY STANDARD UPLOADER — RAG COMPLIANCE ENGINE
          </h4>
        </div>

        <div className="mb-[12px]">
          <label className="block text-[10px] text-[#8B949E] font-mono-tech uppercase mb-[4px]">
            Standard Name (Optional)
          </label>
          <input
            type="text"
            value={standardName}
            onChange={(e) => setStandardName(e.target.value)}
            placeholder="e.g. OISD-STD-116 Amendment 2026, DGMS Safety Circular No. 12"
            className="w-full px-[10px] py-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[12px] font-mono-tech text-[#E6EDF3] focus:outline-none focus:border-[#58A6FF] placeholder:text-[#4A5568]"
          />
        </div>

        {/* Drag & Drop Zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`cursor-pointer border-2 border-dashed rounded-[6px] p-[32px] text-center transition-all ${
            isDragging
              ? 'border-[#58A6FF] bg-[#58A6FF]/8'
              : 'border-[#21262D] hover:border-[#58A6FF]/50 hover:bg-[#58A6FF]/5'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.pdf,.md"
            onChange={handleFileChange}
            className="hidden"
          />
          {isUploading ? (
            <div className="flex flex-col items-center gap-[8px]">
              <Loader className="w-[24px] h-[24px] text-[#58A6FF] animate-spin" strokeWidth={1.5} />
              <span className="text-[12px] text-[#58A6FF] font-mono-tech">VECTORISING DOCUMENT...</span>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-[8px]">
              <FileText className="w-[28px] h-[28px] text-[#8B949E]" strokeWidth={1.5} />
              <span className="text-[13px] text-[#E6EDF3] font-mono-tech">
                Drop PDF / TXT standard here or click to browse
              </span>
              <span className="text-[11px] text-[#8B949E] font-sans">
                OISD amendments, DGMS circulars, local refinery bylaws
              </span>
            </div>
          )}
        </div>

        {/* Uploaded Documents List */}
        {uploadedDocs.length > 0 && (
          <div className="mt-[12px] space-y-[6px]">
            <span className="text-[10px] text-[#8B949E] font-mono-tech uppercase">
              Indexed Documents ({uploadedDocs.length})
            </span>
            {uploadedDocs.map((doc) => (
              <div key={doc.doc_id} className="flex items-center justify-between p-[8px] bg-[#0D1117] rounded-[4px] border border-[#21262D] text-[11px] font-mono-tech">
                <div className="flex items-center gap-[8px]">
                  <CheckCircle2 className="w-[12px] h-[12px] text-[#2EA043]" strokeWidth={1.5} />
                  <span className="text-[#E6EDF3]">{doc.standard_name}</span>
                  <span className="text-[#8B949E]">({doc.filename})</span>
                </div>
                <span className="text-[#8B949E]">{doc.total_chunks} chunks · {doc.word_count.toLocaleString()} words</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* RAG Query Interface */}
      <div className="zg-card">
        <div className="flex items-center gap-[8px] mb-[16px] border-b border-[#21262D] pb-[16px]">
          <Search className="w-[18px] h-[18px] text-[#FF6200]" strokeWidth={1.5} />
          <h4 className="text-[13px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            RAG COMPLIANCE QUERY ENGINE
          </h4>
        </div>

        <form onSubmit={handleQuery} className="flex gap-[10px] mb-[16px]">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Query uploaded standards (e.g. 'hot work permit gas detection requirements')"
            className="flex-1 px-[12px] py-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[12px] font-mono-tech text-[#E6EDF3] focus:outline-none focus:border-[#58A6FF] placeholder:text-[#4A5568]"
          />
          <button
            type="submit"
            disabled={isQuerying || !query.trim()}
            className="btn-primary flex items-center gap-[6px] px-[16px] disabled:opacity-50"
          >
            {isQuerying ? (
              <Loader className="w-[13px] h-[13px] animate-spin" strokeWidth={1.5} />
            ) : (
              <Search className="w-[13px] h-[13px]" strokeWidth={1.5} />
            )}
            Query
          </button>
        </form>

        {/* Query Results */}
        {queryResults && (
          <div className="space-y-[10px]">
            {queryResults.message && (
              <div className="p-[10px] text-[11px] font-mono-tech text-[#8B949E] border border-[#21262D] rounded-[4px] bg-[#0D1117]">
                {queryResults.message}
              </div>
            )}
            {queryResults.results?.map((result, i) => (
              <div key={i} className="p-[12px] bg-[#0D1117] border border-[#21262D] rounded-[4px] space-y-[6px]">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-[8px]">
                    <span className="text-[10px] font-mono-tech text-[#8B949E]">{result.doc_id}</span>
                    <span className="text-[11px] font-mono-tech text-[#58A6FF] font-bold">{result.standard_name}</span>
                  </div>
                  <span className="text-[10px] font-mono-tech px-[6px] py-[1px] rounded border border-[#2EA043]/30 text-[#2EA043] bg-[#2EA043]/10">
                    Relevance: {(result.relevance_score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-[11px] text-[#E6EDF3] font-sans leading-[1.5] border-t border-[#21262D] pt-[6px]">
                  {result.passage}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
