import { useEffect, useState } from 'react'
import '../App.css'
import { DocumentUpload, type ExtractionResult } from '../components/DocumentUpload'
import { DetectedValues } from '../components/DetectedValues'
import { NewFormatPanel } from '../components/NewFormatPanel'
import { pingHealth } from '../api/client'

function DemoApp() {
  const [backendReady, setBackendReady] = useState(false)
  const [backendTimeout, setBackendTimeout] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [results, setResults] = useState<ExtractionResult[]>([]);
  const [isNewFormat, setIsNewFormat] = useState(false);
  const [documentType, setDocumentType] = useState('');
  const [fieldList, setFieldList] = useState<string[]>([]);

  useEffect(() => {
    let cancelled = false
    const start = Date.now()
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 1000)

    ;(async () => {
      while (!cancelled) {
        if (await pingHealth()) { if (!cancelled) setBackendReady(true); break }
        if (Date.now() - start > 90_000) { if (!cancelled) setBackendTimeout(true); break }
        await new Promise(r => setTimeout(r, 2500))
      }
      clearInterval(timer)
    })()

    return () => { cancelled = true; clearInterval(timer) }
  }, [])

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      <div className="w-[420px] flex-shrink-0 bg-white border-r border-gray-200 overflow-y-auto">
        <DocumentUpload
          onResult={(r) => setResults(prev => [...prev, r])}
          onIsNewFormatChange={setIsNewFormat}
          documentType={documentType}
          fieldList={fieldList}
        />
      </div>
      <div className="flex-1 overflow-hidden bg-white flex flex-col">
        {!backendReady && (
          <div className={`flex items-center gap-2 px-4 py-2 border-b flex-shrink-0 ${backendTimeout ? "bg-red-50 border-red-100" : "bg-amber-50 border-amber-100"}`}>
            {backendTimeout ? (
              <span className="text-xs text-red-600">バックエンドに接続できませんでした</span>
            ) : (
              <>
                <svg className="w-3.5 h-3.5 text-amber-500 animate-spin flex-shrink-0" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                <span className="text-xs text-amber-700">バックエンド起動中… {elapsed}秒</span>
              </>
            )}
          </div>
        )}
        <div className="flex-1 overflow-hidden">
          {isNewFormat ? (
            <NewFormatPanel
              documentType={documentType}
              onDocumentTypeChange={setDocumentType}
              fieldList={fieldList}
              onFieldListChange={setFieldList}
            />
          ) : (
            <DetectedValues results={results} onClear={() => setResults([])} />
          )}
        </div>
      </div>
    </div>
  )
}

export default DemoApp
