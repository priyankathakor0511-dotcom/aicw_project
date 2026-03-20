async function load(){
 let res = await fetch('/api/dashboard')
 let d = await res.json()

 document.getElementById('total').innerText = d.total
 document.getElementById('present').innerText = d.present
 document.getElementById('leave').innerText = d.leave

 new Chart(document.getElementById('chart'),{
  type:'pie',
  data:{
   labels:['Present','Leave'],
   datasets:[{data:[d.present,d.leave]}]
  }
 })
}

window.onload = load