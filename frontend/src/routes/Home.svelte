<script>
  import svelteLogo from '../assets/svelte.svg'
  import viteLogo from '/vite.svg'
  import Counter from '../lib/Counter.svelte'

  import fastapi from "../lib/api"
  import { link } from 'svelte-spa-router'

  let question_list = []
 /*
  function get_question_list() {
    fetch("http://127.0.0.1:8000/apis/questions/all").then((response) => {
      response.json().then((json) => {
        question_list = json
      })
    })
  }
  */
  function get_question_list() {
    fastapi('get', "/apis/questions/all", {}, (json) => {
            question_list = json
        })
    }

  get_question_list()
</script>

<main>
  <div>
    <div>
      <a href="https://fastapi.tiangolo.com/" target="_blank" rel="noreferrer">
        <img style="width: 500px; height: 180px" src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" class="logo" alt="Vite Logo"/>
      </a>
    </div>
    <a href="https://vite.dev" target="_blank" rel="noreferrer">
      <img src={viteLogo} class="logo" alt="Vite Logo" />
    </a>
    <a href="https://svelte.dev" target="_blank" rel="noreferrer">
      <img src={svelteLogo} class="logo svelte" alt="Svelte Logo" />
    </a>

  </div>
  <h1>Vite + Svelte + FastAPI</h1>

  <div class="card">
    <Counter />
  </div>

  <h3>여기에는 메인페이지 구성을 하면 된다.</h3>
  <br>
  <ul>
  {#each question_list as question}
    <li><a use:link href="/detail/{question.id}">{question.subject}</a></li>
    <li>{question.content}</li>
  {/each}
</ul>

  <p>
    Check out <a href="https://github.com/sveltejs/kit#readme" target="_blank" rel="noreferrer">SvelteKit</a>, the official Svelte app framework powered by Vite!
  </p>

  <p class="read-the-docs">
    Click on the Vite and Svelte logos to learn more
  </p>
</main>

<style>
  .logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
    transition: filter 300ms;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }
  .logo.svelte:hover {
    filter: drop-shadow(0 0 2em #ff3e00aa);
  }
  .read-the-docs {
    color: #888;
  }
</style>


<!--<script>-->
<!--  let message;-->

<!--  fetch("http://127.0.0.1:8000/").then((response) => {-->
<!--    response.json().then((json) => {-->
<!--      message = json.message;-->
<!--    });-->
<!--  });-->
<!--</script>-->

<!--<h1>{message}</h1>-->

<!--<script>-->
<!--  async function hello() {-->
<!--    const res = await fetch("http://127.0.0.1:8000/");-->
<!--    const json = await res.json();-->

<!--    if (res.ok) {-->
<!--      return json.message;-->
<!--    } else {-->
<!--      alert("error");-->
<!--    }-->
<!--  }-->

<!--  let promise = hello();-->
<!--</script>-->

<!--{#await promise}-->
<!--  <p>...waiting</p>-->
<!--{:then message}-->
<!--  <h1>{message}</h1>-->
<!--{/await}-->



