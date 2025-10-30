<script>
    import fastapi from "../lib/api"
    import Error from "../components/Error.svelte"
    import { push } from 'svelte-spa-router'
    import { is_login } from "../lib/store"

    import moment from 'moment/min/moment-with-locales'
    moment.locale('ko')

    export let params = {}
    let question_id = params.question_id
    /*Answer 모델에 Queston 모델을 연결할 때 backref="answers_all" 속성을 지정했기 때문*/
    let question = {answers_all:[]}
    let content = ""
    let error = {detail:[]}

    function get_question() {
        fastapi("get", "/apis/questions/detail/" + question_id, {}, (json) => {
            question = json
        })
    }

    get_question()

    function post_answer(event) {
        event.preventDefault()
        let url = "/apis/answers/post/" + question_id
        let params = {
            content: content
        }
        fastapi('post', url, params,
            (json) => {
                content = ''
                error = {detail:[]}
                get_question()
            },
            (err_json) => {
                error = err_json
            }
        )
    }
</script>


<div class="container my-3">
    <!-- 질문 -->
    <h2 class="border-bottom py-2">{question.subject}</h2>
    <div class="card my-3">
        <div class="card-body">
            <div class="card-text" style="white-space: pre-line;">{question.content}</div>
            <div class="d-flex justify-content-end">
                <div class="badge bg-light text-dark p-2">
                    <div class="mb-2">{ question.author ? question.author.username : ""}</div>
                    <div>{moment.utc(question.created_at).local().format('YYYY-MM-DD HH:mm')}</div>
                </div>
            </div>
        </div>
    </div>
    <p class="text-end"><button class="btn btn-secondary" on:click="{() => {
        push('/')
    }}">목록으로</button></p>
    <!-- 답변 목록 -->
    <h5 class="border-bottom my-3 py-2">{question.answers_all.length}개의 답변이 있습니다.</h5>
    {#each question.answers_all as answer}
    <div class="card my-3">
        <div class="card-body">
            <div class="card-text" style="white-space: pre-line;">{answer.content}</div>
            <div class="d-flex justify-content-end">
                <div class="badge bg-light text-dark p-2">
                    <div class="mb-2">{ answer.author ? answer.author.username : ""}</div>
                    <div>{moment.utc(answer.created_at).local().format('YYYY-MM-DD HH:mm')}</div>
                </div>
            </div>
        </div>
    </div>
    {/each}
    <!-- 답변 등록 -->
    <Error error={error} />
    <form method="post" class="my-3">
        <div class="mb-3">
            <textarea rows="10" bind:value={content} disabled={$is_login ? "" : "disabled"} class="form-control"></textarea>
        </div>
        <p class="text-end"><input type="submit" value="답변등록" class="btn btn-primary {$is_login ? '' : 'disabled'}" on:click="{post_answer}" /></p>
    </form>
</div>