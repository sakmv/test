import { useState,useRef,useEffect } from 'react'
import { FileText, Paperclip, Upload, Search, MessagesSquare, Quote, Sparkles, ScatterChart, Grid3x3, Zap } from "lucide-react";
import './index.css'
import toast, { Toaster } from 'react-hot-toast';
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

const fileInputRef = useRef(null)
const [file,setFile]=useState([])
const [query,setQuery]=useState('')
const [loading,setLoading]=useState(false)
const [sessionId]=useState(getSession)
const [responseList,setResponseList]=useState([])
const[filenames,setFilenames]=useState([])

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
    const sim= await fetch(`${BASE_URL}/visual`,{
      method:'POST',
      mode:'cors',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({ses:sessionId}),
    })
    if(!sim.ok){
      throw new Error(`${sim.status}`)
    }
    const mat = sim.json()
  }
  catch(error){
    toast.error(`${error}`)
  }
  finally{
    setLoading(false)
  }
}

return (
  <div className="bg-gradient-to-b from-stone-50 to-stone-100 min-h-screen w-full text-stone-900 flex flex-col items-center px-6 py-16 gap-10">
    <Toaster />

    {/* Header */}
    <div className="w-full flex flex-col items-center gap-3">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-stone-800 to-stone-900 flex items-center justify-center shadow-lg shadow-stone-900/20">
          <FileText size={20} className="text-white" />
        </div>
        <h1 className="text-3xl font-semibold tracking-tight text-stone-900">docmind</h1>
      </div>
      <p className="text-sm text-stone-500 tracking-wide">Document intelligence, grounded in your sources</p>
    </div>

    {/* Main Input Card */}
    <div className="w-full max-w-4xl bg-white border border-stone-200/80 rounded-2xl p-6 shadow-sm shadow-stone-200/50 flex flex-col gap-5">

      {/* File Upload Row */}
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold text-stone-400 uppercase tracking-wider w-16">Files</span>
        <div className="flex-1 flex items-center gap-3">
          <label className="bg-stone-50 hover:bg-stone-100 text-stone-600 text-sm rounded-xl py-2.5 px-5 cursor-pointer transition-all border border-stone-200 hover:border-stone-300 flex items-center gap-2 font-medium">
            <Paperclip size={15} />
            Browse
            <input
              className="hidden"
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt"
              multiple
              onChange={(e) => setFile([...e.target.files])}
            />
          </label>
          <button
            className="bg-stone-900 hover:bg-stone-800 disabled:bg-stone-300 disabled:cursor-not-allowed text-white text-sm font-medium rounded-xl py-2.5 px-5 transition-all flex items-center gap-2 shadow-sm hover:shadow-md"
            onClick={uploadFile}
            disabled={loading}
          >
            <Upload size={15} />
            Upload
          </button>
        </div>
      </div>

      {/* Selected but not yet uploaded */}
      {file.length > 0 && (
        <div className="flex flex-col gap-2">
          <span className="text-xs font-semibold text-stone-400 uppercase tracking-wider">Ready to upload</span>
          <div className="flex flex-wrap gap-2">
            {file.map((f, idx) => (
              <div key={idx} className="flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-lg text-xs font-medium border border-blue-200">
                <span>{f.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Uploaded Files List */}
      {filenames.length > 0 && (
        <div className="flex flex-col gap-2">
          <span className="text-xs font-semibold text-stone-400 uppercase tracking-wider">Uploaded Files</span>
          <div className="flex flex-wrap gap-2">
            {filenames.map((name, idx) => (
              <div key={idx} className="flex items-center gap-2 bg-stone-100 text-stone-700 px-3 py-1 rounded-lg text-xs font-medium border border-stone-200">
                <span>{name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Divider */}
      <div className="h-px bg-stone-100" />

      {/* Query Row */}
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold text-stone-400 uppercase tracking-wider w-16">Ask</span>
        <div className="flex-1 flex items-center gap-3">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-stone-400" />
            <input
              className="w-full bg-stone-50 border border-stone-200 rounded-xl pl-11 pr-4 py-3 text-sm text-stone-800 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10 focus:border-stone-300 transition-all"
              type="text"
              placeholder="Ask something about your documents...(only .pdf, .txt)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && queryAsk()}
            />
          </div>
          <button
            className="bg-stone-900 hover:bg-stone-800 disabled:bg-stone-300 disabled:cursor-not-allowed text-white text-sm font-medium rounded-xl px-6 py-3 transition-all shadow-sm hover:shadow-md"
            onClick={queryAsk}
            disabled={loading}
          >
            Go
          </button>
        </div>
      </div>
    </div>

    {/* Results Grid */}
    <div className="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-2 gap-5">
      {/* Responses Panel */}
      <div className="bg-white border border-stone-200/80 rounded-2xl p-6 flex flex-col gap-4 shadow-sm shadow-stone-200/50">
        <div className="flex items-center gap-2 pb-2 border-b border-stone-100">
          <MessagesSquare size={16} className="text-stone-500" />
          <span className="text-sm font-semibold text-stone-700">Responses</span>
          {responseList.length > 0 && (
            <span className="ml-auto text-xs bg-stone-100 text-stone-500 px-2 py-0.5 rounded-full font-medium">
              {responseList.length}
            </span>
          )}
        </div>
        <ul className="flex flex-col gap-3 max-h-80 overflow-y-auto">
          {responseList.map((res, index) => (
            <li key={index} className="list-none bg-stone-50 rounded-xl p-4 border border-stone-100">
              <div className="flex items-start gap-2 mb-3">
                <div className="w-5 h-5 rounded-full bg-stone-200 flex items-center justify-center shrink-0 mt-0.5">
                  <span className="text-[10px] font-bold text-stone-500">Q</span>
                </div>
                <p className="text-sm font-medium text-stone-800 leading-relaxed">{res.query}</p>
              </div>
              <div className="pl-7">
                <p className="text-sm text-stone-600 leading-relaxed">{res.response}</p>
              </div>
            </li>
          ))}
          {responseList.length === 0 && (
            <li className="text-center py-8 text-stone-400 text-sm">No responses yet</li>
          )}
        </ul>
      </div>

      {/* Citations Panel */}
      <div className="bg-white border border-stone-200/80 rounded-2xl p-6 flex flex-col gap-4 shadow-sm shadow-stone-200/50">
        <div className="flex items-center gap-2 pb-2 border-b border-stone-100">
          <Quote size={16} className="text-amber-600" />
          <span className="text-sm font-semibold text-stone-700">Source Citations</span>
        </div>
        <ul className="flex flex-col gap-3 max-h-80 overflow-y-auto">
          {responseList.map((res, i) => (
            <li key={i} className="list-none bg-amber-50/80 rounded-xl p-4 border-l-4 border-amber-400">
              <p className="font-serif text-sm text-stone-700 leading-relaxed italic">"{res.source}"</p>
            </li>
          ))}
          {responseList.length === 0 && (
            <li className="text-center py-8 text-stone-400 text-sm">Citations will appear here</li>
          )}
        </ul>
      </div>
    </div>

    {/* Visualizations Section */}
    <div className="w-full max-w-4xl flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <div className="flex-1 h-px bg-gradient-to-r from-transparent to-stone-200" />
        <div className="flex items-center gap-2 px-4 py-1.5 bg-stone-100 rounded-full">
          <Sparkles size={14} className="text-stone-500" />
          <span className="text-xs font-semibold text-stone-500 uppercase tracking-wider">Visualizations</span>
        </div>
        <div className="flex-1 h-px bg-gradient-to-l from-transparent to-stone-200" />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="h-56 bg-white border border-stone-200/80 rounded-2xl flex flex-col items-center justify-center gap-3 shadow-sm shadow-stone-200/50 hover:shadow-md transition-shadow cursor-pointer group">
          <div className="w-12 h-12 rounded-xl bg-stone-100 flex items-center justify-center group-hover:bg-stone-200 transition-colors">
            <ScatterChart size={24} className="text-stone-500" />
          </div>
          <span className="text-sm font-medium text-stone-600">PCA Scatter</span>
          <span className="text-xs text-stone-400">Dimensionality reduction</span>
        </div>
        <div className="h-56 bg-white border border-stone-200/80 rounded-2xl flex flex-col items-center justify-center gap-3 shadow-sm shadow-stone-200/50 hover:shadow-md transition-shadow cursor-pointer group">
          <div className="w-12 h-12 rounded-xl bg-stone-100 flex items-center justify-center group-hover:bg-stone-200 transition-colors">
            <Grid3x3 size={24} className="text-stone-500" />
          </div>
          <span className="text-sm font-medium text-stone-600">Heatmap</span>
          <span className="text-xs text-stone-400">Correlation matrix</span>
        </div>
      </div>
      <div className="flex justify-center">
        <button onClick={visual} className="bg-gradient-to-r from-stone-800 to-stone-900 hover:from-stone-700 hover:to-stone-800 text-white text-sm font-medium rounded-xl px-8 py-3 transition-all shadow-lg shadow-stone-900/20 hover:shadow-xl flex items-center gap-2">
          Generate
        </button>
      </div>
    </div>
  </div>
)
}
export default App