<script>
    import fastapiLogo from '../assets/fastapi.png'
    import svelteLogo from '../assets/svelte.png'
    import viteLogo from '/vite.png'
    import Counter from '../lib/Counter.svelte'

    import fastapi from "../lib/api"
    import {link} from 'svelte-spa-router'
    import {page} from "../lib/store"

    import moment from 'moment/min/moment-with-locales'
    moment.locale('ko')

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
    let size = 10
    // let page = 0
    let total = 0
    $: total_page = Math.ceil(total / size)

    function get_question_list(_page = 0) {
        let params = {
            page: _page,
            size: size,
        }
        fastapi('get', '/apis/questions/all', params, (json) => {
            question_list = json.question_list
            $page = _page
            total = json.total
        })
    }

    $: get_question_list($page)
</script>

<main class="container">
    <div class="text-center">
        <a href="https://fastapi.tiangolo.com/" target="_blank" rel="noreferrer">
            <img style="width: 275px; height: 100px" src={fastapiLogo} class="logo" alt="Vite Logo"/>
        </a>
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
                    <td>{ total - ($page * size) - i }: {question.id}</td>
                    <td>
                        <a use:link href="/detail/{question.id}">{question.subject}</a>
                        <!--
                        {#if question.answers_all.length > 0 }
                            <span class="text-danger small mx-2">{question.answers_all.length}</span>
                        {/if}
                        -->
                        <!--- 위처럼해도 작동은 한다.
                        question.answers_all가 아직 없거나(undefined/null) 배열이 아닌 경우를 대비해서....
                        이런 경우에 .length에 접근하면 에러가 나거나 조건이 제대로 평가되지 않습니다.
                        안전하게 고치기 아래처럼 안전한 접근으로 바꾸면 됩니다.
                        -->
                        {#if (question.answers_all?.length ?? 0) > 0}
                            <span class="text-danger small mx-2">{question.answers_all?.length}</span>
                        {/if}

                    </td>
                    <td>{moment.utc(question.created_at).local().format('YYYY-MM-DD HH:mm')}</td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>

    <!-- 페이징처리 시작 -->
    <ul class="pagination justify-content-center">
        <!-- 이전페이지 -->
        <li class="page-item {$page <= 0 && 'disabled'}">
            <button class="page-link" on:click="{() => get_question_list($page-1)}">이전</button>
        </li>
        <!-- 페이지번호 -->
        {#each Array(total_page) as _, loop_page}

            <!--{#if loop_page >= $page - 1 && loop_page <= page + 4} -->
            <!--페이지가 5개씩 배치되게 하기위해서 0을 넣어서 loop_page >= page (- 0), 4를 넣었다.-->
            {#if loop_page >= $page && loop_page <= $page + 4}
                <li class="page-item {loop_page === $page && 'active'}">
                    <button on:click="{() => get_question_list(loop_page)}" class="page-link">{loop_page + 1}</button>
                </li>
            {/if}
            <!--지금까지 만든 페이징 기능에 '처음'과 '마지막' 링크를 추가하고 '…' 생략 기호까지 추가하면 더 완성도 높은 페이징 기능이 될 것이다.-->
        {/each}
        <!-- 다음페이지 -->
        <li class="page-item {$page >= total_page-1 && 'disabled'}">
            <button class="page-link" on:click="{() => get_question_list($page+1)}">다음</button>
        </li>
    </ul>
    <!-- 페이징처리 끝 -->

    <p class="text-end"><a use:link href="/question-post" class="btn btn-primary">질문 등록하기</a></p>

    <p class="text-center">
        Check out <a href="https://github.com/sveltejs/kit#readme" target="_blank" rel="noreferrer">SvelteKit</a>, the official Svelte app framework powered by Vite!
    </p>

    <div class="text-center">
        <Counter/>
    </div>

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



