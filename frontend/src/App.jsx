import { useState,useRef,useEffect } from 'react'
import {Download, X,FileText, Paperclip, Upload, Search, MessagesSquare, Quote, Sparkles, ScatterChart, Grid3x3, Zap } from "lucide-react";
import './index.css'
import toast, { Toaster } from 'react-hot-toast';
import Plot from 'react-plotly.js'

const BASE_URL = 'http://127.0.0.1:8000'



function App() {
const getSession =()=>{
  let sid= localStorage.getItem("sessionid")
  if (!sid){
    sid=crypto.randomUUID()
    localStorage.setItem("sessionid",sid)
  }
  return sid
}
const[claim,setClaim]=useState(null)
const[uploadLoad,setUploadLoad]=useState(false)
const [visible,setVisible]=useState(true)
const fileInputRef = useRef(null)
const [file,setFile]=useState([])
const [query,setQuery]=useState('')
const [loading,setLoading]=useState(false)
const [sessionId]=useState(getSession)
const [responseList,setResponseList]=useState([])
const[filenames,setFilenames]=useState([])
const[matrix,setMatrix]=useState([])
const[columns,setColumns]=useState([])
const [pca, setPca] = useState([])
const [generating,setGenerating]=useState(false)
const[userClaim,setUserClaim]=useState("")

const getFiles = async ()=>{
  const f = await fetch(`${BASE_URL}/files`,{
    method:'POST',
    mode:'cors',
    body:JSON.stringify({ses:sessionId}),
    headers:{'Content-Type':'application/json'}
  })
  const data= await f.json()
  setFilenames(data.fileSet)
}

useEffect(() => {
  getFiles()
}, [])

const uploadFile = async ()=>{
  if(file.length==0){
    toast.error("Select a file")
    return
  }
  const formdata=new FormData()
  formdata.append("sessionid",sessionId)
  file.forEach((f)=>formdata.append("file",f))
  try{
    setUploadLoad(true)
    setLoading(true)
    const stat = await fetch(`${BASE_URL}/upload`,{
      method:'POST',
      body:formdata,
      mode:'cors'
    })
    if(!stat.ok){
      throw new Error(`${stat.status}`)
    }
    const data =await stat.json()
    console.log(data)
    toast.success(`Uploaded ${data.filename.join(", ")}`)
    await getFiles()
    setFile([])
    if (fileInputRef.current) fileInputRef.current.value = ""
  }
  catch(err){
    toast.error(`error ${err}`)
    return
  }
  finally{
    setLoading(false)
    setUploadLoad(false)
  }
}

const queryAsk = async ()=>{
  if(query.trim()){
  try{
    setLoading(true)
    setResponseList(prev => [{query, response:"", source:""}, ...prev])
    const res = await fetch(`${BASE_URL}/query`,{
      method:"POST",
      headers:{'Content-Type':'application/json'},
      mode:'cors',
      body:JSON.stringify({text:query,sessionid:sessionId,memory:responseList})
      })
      if(!res.ok){
        throw new Error(`${res.status}`)
      }
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      while(true){
        const {value, done} = await reader.read()
        if(done) break
        const lines = decoder.decode(value).split("\n").filter(l => l.startsWith("data: "))
        for(const line of lines){
          const json = JSON.parse(line.replace("data: ",""))
          if(json.done) break
          setResponseList(prev => {
            const updated = [...prev]
            if(json.type === "answer"){
              updated[0] = {...updated[0], response: updated[0].response + json.token}
            } else if(json.type === "source"){
              updated[0] = {...updated[0], source: updated[0].source + json.token}
            }
            return updated
          })
        }
      }
    }
    catch(err){
      toast.error(`${err}`)
      return
    }
    finally{
      setQuery('')
      setLoading(false)
    }
  }
}

const visual=async()=>{
  try{
    setLoading(true)
    setGenerating(true)
    if(filenames.length==0){
      toast.error('No chunks Generated. Upload a file')
      return
    }
    const sim= await fetch(`${BASE_URL}/visual`,{
      method:'POST',
      mode:'cors',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({ses:sessionId}),
    })
    if(!sim.ok){
      throw new Error(`${sim.status}`)
    }
    const mat = await sim.json()
    setMatrix(mat.matt)
    setPca(mat.pca)
    setVisible(false)  
    
  }
  catch(error){
    toast.error(`${error}`)
  }
  finally{
    setLoading(false)
    setGenerating(false)
  }
}

const claims = async ()=>{
  try{
    setLoading(true)
  const res = await fetch(`${BASE_URL}/claim`,{
    method:"POST",
    mode:"cors",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({text:query,sessionid:sessionId,memory:responseList})
  })
  if(!res.ok){
    toast.error(res.status)
    throw new Error(`${res.status}`)
  }
  const data = await res.json()
  setClaim({"label":data.label,"documents":data.documents})
}catch(err){
  toast.error(`${err}`)
  return
}finally{
setLoading(false)
}
}


const download= async ()=>{
  try{
    setLoading(true)
  const status = await fetch(`${BASE_URL}/download`,{
    method:"POST",
    mode:"cors",
    body:JSON.stringify({res:responseList}),
    headers:{'Content-Type':'application/json'}
  })
  if(!status.ok){
    throw new Error(`${status.status}`)
  }
   const blob = await status.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'notemind_session.txt'
    document.body.appendChild(a)
    a.click()
    a.remove()

}
  catch(err){
    toast.error(`${err}`)
    return
  } finally{
    setLoading(false)
  }

}


return (
<>
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=Lora:ital,wght@0,400;0,500;1,400&family=Space+Mono:wght@400;700&display=swap');
    .dm-root { font-family:'Lora',serif; }
    .dm-display { font-family:'Libre Caslon Text',serif; }
    .dm-mono { font-family:'Space Mono',monospace; }
    .dm-paper { background:#FAF6EC repeating-linear-gradient(transparent 0 31px, rgba(63,91,69,.05) 31px 32px); }
    .dm-scroll::-webkit-scrollbar{width:6px}
    .dm-scroll::-webkit-scrollbar-thumb{background:rgba(63,91,69,.25);border-radius:99px}
    .dm-mark {
      background: linear-gradient(104deg, transparent 0%, #FFE066 6%, #FFD94D 50%, #FFE066 94%, transparent 100%);
      background-repeat: no-repeat;
      padding: 0.15em 0.35em;
      border-radius: 2px;
      box-decoration-break: clone;
      -webkit-box-decoration-break: clone;
    }
    @keyframes shimmer {
      0% { background-position: -600px 0; }
      100% { background-position: 600px 0; }
    }
    .dm-skeleton {
      background: linear-gradient(90deg, #F4EFE2 25%, #EDE6D4 50%, #F4EFE2 75%);
      background-size: 600px 100%;
      animation: shimmer 1.6s infinite linear;
      border-radius: 4px;
    }
    @keyframes indeterminate {
      0% { margin-left: -40%; width: 40%; }
      100% { margin-left: 100%; width: 40%; }
    }
    .dm-indeterminate {
      animation: indeterminate 1.4s ease-in-out infinite;
    }
  `}</style>

  <div className="dm-root dm-paper min-h-screen w-full text-[#2B2A25] flex flex-col items-center px-6 py-16 gap-10">
    <Toaster />
    {/* Page header strip */}
    <div className="w-full max-w-3xl mt-4 border border-[#D8D2BD] rounded-sm px-4 py-2 flex items-center gap-3">
      <span className="dm-mono text-[10px] font-bold text-[#3F5B45] uppercase tracking-widest shrink-0">Title:</span>
      <a className="dm-mono text-[10px] font-bold text-[#3F5B45] uppercase tracking-widest shrink-0" href='https://github.com/sakmv/test'>github_sakmv</a>
      <div className="flex-1 border-b border-dotted border-[#C9C2AE]" />
      <span className="dm-mono text-[10px] text-[#8C8775]">noteMind — 6/26</span>
    </div>

    {/* Masthead */}
    <div className="w-full flex flex-col items-center gap-2 text-center">
      <span className="dm-mono text-[10px] uppercase tracking-[0.3em] text-[#C1652F]">Vol. I — Field Notes</span>
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-[#3F5B45] flex items-center justify-center shadow-sm">
          <FileText size={18} className="text-[#FAF6EC]" />
        </div>
        <h1 className="dm-display text-4xl tracking-tight">noteMind</h1>
      </div>
      <p className="text-sm text-[#5C5848] italic">document intelligence, grounded in your sources</p>
      <div className="w-20 h-px bg-[#C9C2AE] mt-1" />
    </div>

    {/* Intake Card */}
    <div className="w-full max-w-3xl bg-white border border-[#E5DFCB] rounded-md p-6 shadow-[0_8px_30px_-12px_rgba(63,91,69,.25)] flex flex-col gap-5">

      <div className="flex items-center gap-3">
        <span className="dm-mono text-[10px] font-bold text-[#3F5B45] uppercase tracking-wider w-16">Files</span>
        <div className="flex-1 flex items-center gap-3">
          <label className="bg-[#FAF6EC] hover:bg-[#F2EBD8] text-sm rounded-md py-2.5 px-5 cursor-pointer border border-[#E5DFCB] hover:border-[#C9C2AE] flex items-center gap-2 font-medium transition-all">
            <Paperclip size={15} className="text-[#3F5B45]" /> Browse
            <input className="hidden" ref={fileInputRef} type="file" accept=".pdf,.txt" multiple
              onChange={(e) => setFile([...e.target.files])} />
          </label>
          <button className="bg-[#3F5B45] hover:bg-[#34492c] disabled:bg-[#B9B6A8] text-[#FAF6EC] text-sm font-medium rounded-md py-2.5 px-5 flex items-center gap-2 shadow-sm transition-all"
            onClick={uploadFile} disabled={loading}>
            <Upload size={15} /> Upload
          </button>
        </div>
      </div>

      {file.length > 0 && (
        <div className="flex flex-col gap-1.5 pl-[4.5rem]">
          <span className="dm-mono text-[9px] uppercase tracking-wider text-[#C1652F]">Selected</span>
          <div className="flex flex-wrap gap-2">
            {file.map((f, idx) => (
              <span key={idx} className="dm-mono text-xs bg-[#EFE4D4] text-[#8A4A1F] px-3 py-1 rounded-md border border-[#C1652F]/30">{f.name}</span>
            ))}
          </div>
        </div>
      )}

      {filenames.length > 0 && (
        <div className="flex flex-col gap-1.5 pl-[4.5rem]">
          <span className="dm-mono text-[9px] uppercase tracking-wider text-[#3F5B45]">Uploaded</span>
          <div className="flex flex-wrap gap-2">
            {filenames.map((name, idx) => (
              <span key={idx} className="dm-mono text-xs bg-[#F4F0E4] px-3 py-1 rounded-md border border-[#E5DFCB]">{name}</span>
            ))}
          </div>
        </div>
      )}

      {uploadLoad && (
        <div className="pl-[4.5rem] overflow-hidden">
          <div className="w-full h-0.5 bg-[#E5DFCB] rounded-full overflow-hidden">
            <div className="h-full bg-[#3F5B45] rounded-full dm-indeterminate" />
          </div>
        </div>
      )}

      <div className="h-px bg-[#EFE9D8]" />

      <div className="flex items-center gap-3">
        <span className="dm-mono text-[10px] font-bold text-[#3F5B45] uppercase tracking-wider w-16">Ask</span>
        <div className="flex-1 flex items-center gap-3">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8C8775]" />
            <input
              className="w-full bg-[#FAF6EC] border border-[#E5DFCB] rounded-md pl-11 pr-4 py-3 text-sm placeholder-[#8C8775] focus:outline-none focus:ring-1 focus:ring-[#3F5B45]/40 focus:border-[#3F5B45]/50 transition-all"
              type="text" placeholder="Ask something about your documents...(only .pdf, .txt)"
              value={query} onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && queryAsk()} />
          </div>
          <button className="bg-[#C1652F] hover:bg-[#a8551f] disabled:bg-[#B9B6A8] text-white text-sm font-medium rounded-md px-6 py-3 shadow-sm transition-all"
            onClick={queryAsk} disabled={loading}>Go</button>
        </div>
      </div>
    </div>

    {/* Entries Feed */}
    <div className="w-full max-w-3xl flex flex-col gap-4">
      <div className="flex items-center gap-2 px-1">
        <MessagesSquare size={14} className="text-[#3F5B45]" />
        <span className="dm-mono text-[10px] font-bold text-[#3F5B45] uppercase tracking-wider">Entries</span>
        {responseList.length > 0 && <span className="dm-mono text-[10px] text-[#8C8775]">({responseList.length})</span>}
        <div className="flex-1 h-px bg-[#E5DFCB] ml-2" />
        {responseList.length > 0 && (
          <button
            onClick={download}
            disabled={loading}
            className="dm-mono text-[9px] font-bold text-[#3F5B45] uppercase tracking-wider flex items-center gap-1.5 hover:text-[#C1652F] disabled:text-[#B9B6A8] transition-all">
            <Download size={12} /> Export
          </button>
        )}
      </div>

      <div className="dm-scroll flex flex-col gap-4 max-h-[34rem] overflow-y-auto pr-1">
        {responseList.map((res, index) => (
          <div key={index} className="bg-white border border-[#E5DFCB] rounded-md p-5 flex flex-col gap-3 shadow-[0_6px_20px_-14px_rgba(63,91,69,.3)]">
            <div className="flex items-start gap-2">
              <span className="dm-display text-[#C9C2AE] text-lg leading-none select-none">{String(index + 1).padStart(2, '0')}</span>
              <p className="text-sm font-semibold leading-relaxed pt-0.5">{res.query}</p>
            </div>
            <p className="text-sm text-[#4A4738] leading-relaxed pl-7">{res.response}</p>
            <p className="dm-display italic text-[14px] text-[#3a2f1c] leading-relaxed pl-7">
              <Quote size={11} className="inline text-[#d7b65d] -mt-1 mr-1" />
              <span className="dm-mark">{res.source}</span>
            </p>
          </div>
        ))}

        {responseList.length === 0 && (
          <div className="bg-white border border-dashed border-[#D8D2BD] rounded-md py-12 flex flex-col items-center gap-2">
            <Quote size={18} className="text-[#C9C2AE]" />
            <span className="text-sm text-[#8C8775] italic">The page is blank — ask something to begin the entry.</span>
          </div>
        )}
      </div>
    </div>

    {/*Figures */}
    <div className="w-full max-w-3xl flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <div className="flex-1 h-px bg-[#E5DFCB]" />
        <div className="flex items-center gap-2 px-4 py-1.5 bg-[#F2EBD8] rounded-full border border-[#E5DFCB]">
          <Sparkles size={13} className="text-[#3F5B45]" />
          <span className="dm-mono text-[10px] font-bold text-[#3F5B45] uppercase tracking-wider">Analytic Figures</span>
        </div>
        <div className="flex-1 h-px bg-[#E5DFCB]" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {[
          { label: 'Fig. 1 — Chunk Cosine Similarity Heatmap', data: matrix.length > 0 && [{ z: matrix, type: 'heatmap', colorscale: [[0,'#FAF6EC'],[0.35,'#E9D9BE'],[0.65,'#C1652F'],[1,'#3F5B45']] }], icon: ScatterChart },
          { label: 'Fig. 2 — Dimensionally Reduced Scatter Plot', data: pca.length > 0 && [{
              x: pca.map(p => p.x), y: pca.map(p => p.y), text: pca.map(p => p.label),
              mode: 'markers+text', type: 'scatter', textposition: 'top center',
              textfont: { size: 9, color: '#8C8775' },
              marker: { size: 8, color: pca.map((_, i) => i), colorscale: [[0,'#FAF6EC'],[0.35,'#E9D9BE'],[0.65,'#C1652F'],[1,'#3F5B45']] },
            }], icon: Grid3x3 },
        ].map(({ label, data, icon: Icon }, i) => (
          <div key={i} className="bg-white border border-[#E5DFCB] rounded-md p-4 shadow-[0_6px_20px_-14px_rgba(63,91,69,.3)]">
            <span className="dm-mono text-[10px] text-[#8C8775] mb-2 block uppercase tracking-wider">{label}</span>

            {generating ? (
              <div className="h-56 flex flex-col justify-end gap-2 px-2 pb-3 pt-4">
                <div className="flex items-end gap-1.5 h-full">
                  {Array.from({ length: 10 }).map((_, j) => (
                    <div
                      key={j}
                      className="dm-skeleton flex-1 rounded-sm"
                      style={{ height: `${30 + Math.sin(j * 1.3 + i) * 25 + 25}%`, animationDelay: `${j * 0.07}s` }}
                    />
                  ))}
                </div>
                <div className="dm-skeleton h-2 w-3/4 mx-auto mt-2" style={{ animationDelay: '0.3s' }} />
                <div className="dm-skeleton h-2 w-1/2 mx-auto" style={{ animationDelay: '0.5s' }} />
              </div>
            ) : data ? (
              <Plot data={data} useResizeHandler style={{ width: '100%' }} layout={{
                autosize: true, height: 280, margin: { t: 10, r: 10, b: 40, l: 40 },
                paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#8C8775' },
                ...(i === 1 ? {
                  xaxis: { title: { text: 'PC1' }, gridcolor: 'rgba(63,91,69,.12)' },
                  yaxis: { title: { text: 'PC2' }, gridcolor: 'rgba(63,91,69,.12)' },
                } : {}),
              }} />
            ) : (
              <div className="h-56 flex flex-col items-center justify-center gap-3">
                <div className="w-12 h-12 rounded-full bg-[#FAF6EC] border border-[#E5DFCB] flex items-center justify-center">
                  <Icon size={20} className="text-[#3F5B45]" />
                </div>
                <span className="text-sm text-[#8C8775] italic">Click Generate to load</span>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="flex justify-center">
        <button
          onClick={() => { visual(); setVisible(false); }}
          disabled={loading || generating}
          className="dm-mono bg-[#3F5B45] hover:bg-[#34492c] disabled:bg-[#B9B6A8] text-[#FAF6EC] text-xs font-bold uppercase tracking-wider rounded-md px-8 py-3 shadow-sm flex items-center gap-2 transition-all">
          {generating ? (
            <>
              <svg className="animate-spin" width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
              </svg>
              Generating…
            </>
          ) : 'Generate'}
        </button>
      </div>
    </div>

    {/* Claim Verification */}
    <div className="w-full max-w-3xl flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <div className="flex-1 h-px bg-[#E5DFCB]" />
        <div className="flex items-center gap-2 px-4 py-1.5 bg-[#F2EBD8] rounded-full border border-[#E5DFCB]">
          <Sparkles size={13} className="text-[#3F5B45]" />
          <span className="dm-mono text-[10px] font-bold text-[#3F5B45] uppercase tracking-wider">Claim Verification</span>
        </div>
        <div className="flex-1 h-px bg-[#E5DFCB]" />
      </div>

      <div className="w-full bg-white border border-[#E5DFCB] rounded-md overflow-hidden shadow-[0_8px_30px_-12px_rgba(63,91,69,.25)]">

        <div className="p-7 flex flex-col gap-3">
          <span className="dm-mono text-[9px] uppercase tracking-widest text-[#8C8775]">Claim</span>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8C8775]" />
              <input
                className="w-full bg-[#FAF6EC] border border-[#E5DFCB] rounded-md pl-11 pr-4 py-3 text-sm text-[#2B2A25] placeholder-[#8C8775] focus:outline-none focus:ring-1 focus:ring-[#3F5B45]/40 focus:border-[#3F5B45]/50 transition-all"
                style={{fontFamily:"'Lora',serif"}}
                type="text" placeholder="Enter a claim to verify against your documents..."
                value={query} onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && claims()} />
            </div>
            <button
              className="bg-[#FAF6EC] hover:bg-[#F2EBD8] disabled:bg-[#E5DFCB] disabled:text-[#8C8775] text-[#2B2A25] dm-mono text-[10px] font-bold uppercase tracking-wider rounded-md px-6 border border-[#E5DFCB] hover:border-[#C9C2AE] transition-all"
              onClick={claims} disabled={loading}>Verify</button>
          </div>
        </div>

        <div className="h-px bg-[#EFE9D8]" />

        {claim ? (
          <div className="p-7 flex flex-col gap-5">
            <div className="flex items-center gap-3">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-sm ${
                claim.label === 'entailment' ? 'bg-[#EAF3DE] text-[#3F5B45]' :
                claim.label === 'contradiction' ? 'bg-[#FAE8E0] text-[#C1652F]' : 'bg-[#F4F0E4] text-[#8C8775]'
              }`}>
                {claim.label === 'entailment' ? '✓' : claim.label === 'contradiction' ? '✗' : '—'}
              </div>
              <span className={`dm-mono text-[10px] uppercase tracking-widest font-bold ${
                claim.label === 'entailment' ? 'text-[#3F5B45]' :
                claim.label === 'contradiction' ? 'text-[#C1652F]' : 'text-[#8C8775]'
              }`}>
                {claim.label === 'entailment' ? 'Supported' :
                 claim.label === 'contradiction' ? 'Contradicted' : 'Not Found'}
              </span>
              <div className="flex-1 h-px bg-[#EFE9D8]" />
            </div>

            <div className="flex flex-col gap-2">
              <span className="dm-mono text-[9px] uppercase tracking-widest text-[#8C8775]">Supporting passage</span>
              <div className={`bg-[#FAF6EC] border border-[#E5DFCB] rounded-r-md p-4 ${
                claim.label === 'entailment' ? 'border-l-2 border-l-[#3F5B45]' :
                claim.label === 'contradiction' ? 'border-l-2 border-l-[#C1652F]' : 'border-l-2 border-l-[#8C8775]'
              }`}>
                <p className="dm-display italic text-sm text-[#5C5848] leading-relaxed">
                  <Quote size={11} className="inline text-[#C9C2AE] -mt-1 mr-1" />
                  {claim.documents}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-7 flex items-center justify-center opacity-40">
            <span className="dm-display italic text-sm text-[#8C8775]">Verdict will appear here</span>
          </div>
        )}
      </div>
    </div>

    {/* Capabilities */}
    <div className="w-full max-w-3xl flex flex-wrap items-center justify-center gap-2.5">
      {[
        { label: 'Custom-Trained Encoder', icon: Sparkles },
        { label: 'Hybrid Retrieval', icon: Search },
        { label: 'Cross-Encoder Reranking', icon: ScatterChart },
        { label: 'Claim Verification', icon: Quote },
        { label: 'Streaming Responses', icon: MessagesSquare },
      ].map(({ label, icon: Icon }, i) => (
        <div key={i} className="flex items-center gap-2 px-4 py-1.5 bg-[#F2EBD8] rounded-full border border-[#C1652F]/40">
          <Icon size={13} className="text-[#C1652F]" />
          <span className="dm-mono text-[10px] font-bold text-[#3F5B45] uppercase tracking-wider">{label}</span>
        </div>
      ))}
    </div>
  </div>

</>
)
}
export default App