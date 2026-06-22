import { useState,useRef } from 'react'
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

    const res = await fetch(`${BASE_URL}/query`,{
      method:"POST",
      headers:{
        'Content-Type':'application/json'},
      mode:'cors',
      body:JSON.stringify({text:query,sessionid:sessionId,memory:responseList})

      })
      if(!res.ok){
        throw new Error(`${res.status}`)
      }
      const data=await res.json()
      setResponseList([{query,response:data.response.trim(),source:data.sources},...responseList])
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
    headers:{
      'Content-Type':'application/json'
    },
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
<div className="bg-orange-50 min-h-screen w-full text-stone-800 flex flex-col items-center px-6 py-10 gap-10 overflow-x-hidden">
  <Toaster/>

  <div className="w-full flex flex-col items-center gap-2">
    <h1 className="text-6xl font-mono font-extrabold text-center tracking-wide text-stone-800">DOCMIND</h1>
    <p className="italic text-stone-500 text-sm">Your go-to document intelligence assistant</p>
  </div>

  
  <div className="w-full max-w-6xl bg-white border border-orange-200 rounded-2xl shadow-md p-6 flex flex-col gap-4">
    <div className="flex items-center gap-3">
      <label className="text-stone-500 text-sm font-medium shrink-0">Select a file</label>
      <label className="bg-orange-50 hover:bg-orange-100 text-stone-700 text-sm font-medium rounded-lg py-2 px-4 cursor-pointer transition-colors border border-orange-200">
        Browse
        <input className="hidden" ref={fileInputRef} type='file' accept=".pdf,.txt" multiple onChange={(e)=>setFile([...e.target.files])}/>
      </label>
      <button className="bg-orange-600 hover:bg-orange-500 disabled:bg-stone-200 disabled:text-stone-400 text-white font-semibold rounded-lg py-2 px-4 transition-colors" onClick={uploadFile} disabled={loading}>Upload</button>
    </div>
    <div className="flex gap-2">
      <input className="flex-1 bg-white border border-orange-200 rounded-lg px-4 py-2 text-stone-800 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-orange-500" type="text" placeholder="Ask something..." value={query} onChange={(e)=>setQuery(e.target.value)}/>
      <button className="bg-orange-600 hover:bg-orange-500 disabled:bg-stone-200 disabled:text-stone-400 text-white font-semibold rounded-lg px-5 transition-colors" onClick={queryAsk} disabled={loading}>Ask</button>
    </div>
  </div>

  
  <div className="w-full max-w-6xl grid grid-cols-2 gap-6">
    <div className="bg-white border border-orange-200 rounded-2xl shadow-md p-6 flex flex-col gap-4">
      <span className="text-stone-500 text-xs font-semibold uppercase tracking-wider">Responses</span>
      <ul className="flex flex-col gap-3">{responseList.map((res,index)=>
        <li key={index} className="list-none bg-orange-50 border border-orange-200 rounded-xl p-4 shadow-sm">
          <pre className="whitespace-pre-wrap font-sans text-orange-700 font-semibold mb-2">Q: {res.query}</pre>
          <pre className="whitespace-pre-wrap font-sans text-stone-400 text-xs font-semibold mb-1">Response:</pre>
          <pre className="whitespace-pre-wrap font-sans text-stone-700">{res.response}</pre>
        </li>)}
      </ul>
    </div>

    <div className="bg-white border border-orange-200 rounded-2xl shadow-md p-6 flex flex-col gap-4">
      <span className="text-stone-500 text-xs font-semibold uppercase tracking-wider">Source Citations</span>
      <ul className="flex flex-col gap-4">{responseList.map((res,i)=>
        <li key={i} className="list-none bg-[#fdf6e3] text-stone-800 rounded-sm shadow-md p-5 border border-amber-200">
          <pre className="whitespace-pre-wrap font-serif text-[15px] leading-relaxed bg-yellow-200/70 px-1 py-0.5 box-decoration-break-clone">{res.source}</pre>
        </li>
      )}</ul>
    </div>
  </div>

  {/* Divider beneath columns */}
  <div className="w-full max-w-6xl h-px bg-orange-300 my-6"></div>

  {/* Graphs Section */}
  <div className="w-full max-w-6xl flex flex-col gap-6 items-center">
    <span className="text-stone-500 text-xs font-semibold uppercase tracking-wider">Visualizations</span>
    <div className="flex w-full gap-6 justify-between">
      <div className="w-1/2 h-64 bg-white border border-orange-200 rounded-xl shadow-md flex items-center justify-center">
        PCA scatter 
      </div>
      <div className="w-1/2 h-64 bg-white border border-orange-200 rounded-xl shadow-md flex items-center justify-center">
        Heatmap
      </div>
    </div>
    <button className="bg-orange-600 hover:bg-orange-500 text-white font-semibold rounded-lg px-6 py-2 transition-colors">
      Generate
    </button>
  </div>
</div>
)

}


export default App