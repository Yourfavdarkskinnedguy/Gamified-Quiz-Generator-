//initializing supabase
const supabaseUrl = 'https://znzdvgcsxggefvgporsm.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpuemR2Z2NzeGdnZWZ2Z3BvcnNtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NjIxMTksImV4cCI6MjA2NzAzODExOX0.Qt8oJbwsl__X978kpum6LSBSbJLHc3HheheGmjzbB70'
const supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);
console.log('supabaseClient:', supabaseClient)


console.log('got here 2')

// Login Function
async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
  
    try {
      const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
      console.log(data)
      if (error) throw error;
      window.location.href = '/chatbot';
    } catch (error) {
      document.getElementById('signup-error-message').innerText = error.message;
    }
  }




//signup
  async function signup() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
  
    try {
      const { data, error } = await supabaseClient.auth.signUp({ email, password });
      console.log(data)
      if (error) throw error;
      window.location.href = '/chatbot';
    } catch (error) {
      document.getElementById('signup-error-message').innerText = error.message;
    }
  }



//enter function for chatbot
function handleSubmit(event) {
    event.preventDefault(); // prevents actual page reload
    const inputValue = document.getElementById("user-input").value;
  }
  