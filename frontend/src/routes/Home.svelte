<script>
   import fastapiLogo from '../assets/fastapi.png'
    import svelteLogo from '../assets/svelte.png'
    import viteLogo from '/vite.png'
    import Counter from '../lib/Counter.svelte'

    import fastapi from "../lib/api"
    import {link} from 'svelte-spa-router'

    let question_list = []

    //  npm i bootstrap@5.3.8
    //  npm install bootstrap@5.3.8

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

<main class="container">
    <div class="text-center">
<!--        <div>-->
            <a href="https://fastapi.tiangolo.com/" target="_blank" rel="noreferrer">
                <img style="width: 275px; height: 100px" src={fastapiLogo} class="logo" alt="Vite Logo"/>
            </a>
<!--        </div>-->
        <a href="https://vite.dev" target="_blank" rel="noreferrer">
            <img src={viteLogo} class="logo" alt="Vite Logo"/>
        </a>
        <a href="https://svelte.dev" target="_blank" rel="noreferrer">
            <img src={svelteLogo} class="logo" alt="Svelte Logo"/>
        </a>

    </div>

    <div class="container my-3">
      <table class="table">
        <thead>
        <tr class="table-dark">
          <th>번호</th>
          <th>제목</th>
          <th>작성일시</th>
        </tr>
        </thead>
        <tbody>
        {#each question_list as question, i}
          <tr>
            <td>{i + 1}</td>
            <td>
              <a use:link href="/detail/{question.id}">{question.subject}</a>
            </td>
            <td>{question.created_at}</td>
          </tr>
        {/each}
        </tbody>
      </table>
    </div>

    <p class="text-end"><a use:link href="/question-post" class="btn btn-primary">질문 등록하기</a></p>

    <p class="text-center">
        Check out <a href="https://github.com/sveltejs/kit#readme" target="_blank" rel="noreferrer">SvelteKit</a>, the official Svelte app framework powered by Vite!
    </p>

    <div class="text-center"><Counter/></div>

    <hr>
    <p class="text-center">
        © FastAPI With Svelte DEV 2025.10.28
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



