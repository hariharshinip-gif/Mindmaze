function sendMessage(){

let input=document.getElementById("userInput")

let msg=input.value

if(msg=="") return

let chat=document.getElementById("chatbox")

chat.innerHTML+=`<p><b>You:</b> ${msg}</p>`

fetch("/chatbot",{

method:"POST",

headers:{"Content-Type":"application/json"},

body:JSON.stringify({message:msg})

})

.then(res=>res.json())

.then(data=>{

chat.innerHTML+=`<p><b>AI:</b> ${data.reply}</p>`

chat.scrollTop=chat.scrollHeight

})

input.value=""

}