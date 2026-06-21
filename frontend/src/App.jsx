import { useState } from 'react'

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
const [file,setFile]=useState([])
const [query,setQuery]=useState('')
const [response,setResponse]=useState('')
const [loading,setLoading]=useState(false)
const [sessionId]=useState(getSession)
const [responseList,setResponseList]=useState([])
const uploadFile = async ()=>{

  if(!file){
    alert("Select a file")
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
    alert(`Uploaded ${data.filename.join(", ")}`)
  }
  catch(err){
    console.log(filename)
    alert(`error ${err}`)
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
      body:JSON.stringify({text:query,sessionid:sessionId})

      })
      if(!res.ok){
        throw new Error(`${res.status}`)
      }
      const data=await res.json()
      setResponseList([...responseList,{query,response:data.response.trim()}])
    }
    catch(err){
      alert("error")
      return
    }
    finally{
      setLoading(false)
    }
  }
}

return(<>
<h1>DOCMIND</h1>
<div>choose file
<input type='file'accept=".pdf,.txt" multiple onChange={(e)=>setFile([...e.target.files])}/><button onClick={uploadFile} disabled={loading}>upload</button>
</div>
<div>
  <input type="text" placeholder="ask" value={query} onChange={(e)=>setQuery(e.target.value)}/><button onClick={queryAsk} disabled={loading}>enter</button>
</div><ul>{responseList.map((res,index)=><><li  style={{ listStyle: 'none', paddingLeft: 0 }} key={index}><pre>Ques. {res.query}</pre></li>
<li key={index} style={{ listStyle: 'none', paddingLeft: 0 }}><pre>{res.response}</pre></li></>)}</ul>
</>)
}


export default App