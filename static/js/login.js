const form=document.getElementById('loginForm');
const msg=document.getElementById('message');
const pass=document.getElementById('password');
const eye=document.getElementById('togglePassword');
const forgot=document.getElementById('forgot');

eye.addEventListener('click',()=>{
  pass.type=pass.type==='password'?'text':'password';
  eye.innerHTML=pass.type==='password'?'<i class="fa-regular fa-eye"></i>':'<i class="fa-regular fa-eye-slash"></i>';
});

forgot.addEventListener('click',(e)=>{
  e.preventDefault();
  msg.className='message';
  msg.textContent='Please contact the Safe Campus administrator to reset your password.';
  msg.classList.add('error');
});

form.addEventListener('submit',async e=>{
  e.preventDefault();
  msg.className='message';
  msg.textContent='Checking login...';
  try{
    const r=await fetch('/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('email').value.trim(),password:pass.value})});
    const d=await r.json();
    if(!d.success){msg.textContent=d.message||'Invalid email or password.';msg.classList.add('error');return;}
    msg.textContent='Login Successful!';msg.classList.add('success');
    setTimeout(()=>location.href=d.redirect,350);
  }catch(err){msg.textContent='Server connection error.';msg.classList.add('error');}
});
