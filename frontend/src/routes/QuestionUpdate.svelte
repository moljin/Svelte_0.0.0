<script>
    import { push } from 'svelte-spa-router'
    import fastapi from "../lib/api"
    import Error from "../components/Error.svelte"
    import QuillEditor from "../components/QuillEditor.svelte";


    export let params = {}
    const question_id = params.question_id

    let error = {detail:[]}
    let subject = ''
    let content = ''

    // Quill 에디터에서 내용 변경 이벤트 발생 시 호출될 함수
    function handleContentChange(html) {
        content = html;

    // function handleContentChange(event) {
        // content = event.detail; // 에디터의 HTML 내용을 content 변수에 저장
        console.log("content:", content);
    }

    fastapi("get", "/apis/questions/detail/" + question_id, {}, (json) => {
        subject = json.subject
        content = json.content
    })

    function update_question(event) {
        event.preventDefault()
        let url = "/apis/questions/update/" + question_id
        let params = {
            question_id: question_id,
            subject: subject,
            content: content,
        }
        fastapi('put', url, params,
            (json) => {
                push('/detail/'+question_id)
            },
            (json_error) => {
                error = json_error
            }
        )
    }
</script>

<div class="container">
    <h5 class="my-3 border-bottom pb-2">질문 수정</h5>
    <Error error={error} />
    <form on:submit|preventDefault={update_question} method="post" class="my-3">
        <div class="mb-3">
            <label for="subject">제목</label>
            <input type="text" class="form-control" bind:value={subject} required
>
        </div>
        <div class="mb-3">
            <label for="content">내용</label>
<!--            <textarea class="form-control" rows="10" bind:value="{content}"></textarea>-->
<!--            <hr>-->
            <!-- Quill 에디터를 넣을 DIV -->
            <div id="quill-container" class="">
                <div id="drop-area"></div>
                <!-- 기존 글 내용(content)을 prop으로 주입 -->
                <QuillEditor content={content} onContentChange={handleContentChange}/>

            </div>
        </div>
<!--        <button class="btn btn-primary" on:click="{update_question}">수정하기</button>-->
        <div class="d-flex gap-2 justify-content-end">
            <button type="submit" class="btn btn-primary">수정하기</button>
            <a class="btn btn-secondary" href={"/detail/" + question_id}>취소</a>
        </div>

    </form>
</div>
