<!--<script>-->
<!--    import fastapi from "../lib/api"-->
<!--    import Error from "../components/Error.svelte"-->
<!--    import { link, push } from 'svelte-spa-router'-->
<!--    import { is_login, username } from "../lib/store"-->

<!--    import moment from 'moment/min/moment-with-locales'-->
<!--    moment.locale('ko')-->

<!--    export let params = {}-->
<!--    let question_id = params.question_id-->
<!--    /*Answer 모델에 Queston 모델을 연결할 때 backref="answers_all" 속성을 지정했기 때문*/-->
<!--    let question = {answers_all:[], voter:[]}//, content: ''}-->
<!--    let content = ""-->
<!--    let error = {detail:[]}-->

<!--    function get_question() {-->
<!--        fastapi("get", "/apis/questions/detail/" + question_id, {}, (json) => {-->
<!--            question = json-->
<!--        })-->
<!--    }-->

<!--    get_question()-->

<!--    // quill 저장내용 quill.getText()-->


<!--    function post_answer(event) {-->
<!--        event.preventDefault()-->
<!--        let url = "/apis/answers/post/" + question_id-->
<!--        let params = {-->
<!--            content: content-->
<!--        }-->
<!--        fastapi('post', url, params,-->
<!--            (json) => {-->
<!--                content = ''-->
<!--                error = {detail:[]}-->
<!--                get_question()-->
<!--            },-->
<!--            (err_json) => {-->
<!--                error = err_json-->
<!--            }-->
<!--        )-->
<!--    }-->

<!--    function delete_question(_question_id) {-->
<!--        if(window.confirm('정말로 삭제하시겠습니까?')) {-->
<!--            let url = "/apis/questions/delete/" + _question_id-->
<!--            let params = {-->
<!--                question_id: _question_id-->
<!--            }-->
<!--            fastapi('delete', url, params,-->
<!--                (json) => {-->
<!--                    push('/')-->
<!--                },-->
<!--                (err_json) => {-->
<!--                    error = err_json-->
<!--                }-->
<!--            )-->
<!--        }-->
<!--    }-->

<!--    function delete_answer(answer_id) {-->
<!--        if(window.confirm('정말로 삭제하시겠습니까?')) {-->
<!--            let url = "/apis/answers/delete/" + answer_id-->
<!--            let params = {-->
<!--                answer_id: answer_id-->
<!--            }-->
<!--            fastapi('delete', url, params,-->
<!--                (json) => {-->
<!--                    get_question()-->
<!--                },-->
<!--                (err_json) => {-->
<!--                    error = err_json-->
<!--                }-->
<!--            )-->
<!--        }-->
<!--    }-->

<!--    function vote_question(_question_id) {-->
<!--        if(window.confirm('정말로 추천하시겠습니까?')) {-->
<!--            let url = "/apis/questions/vote/" + _question_id-->
<!--            let params = {-->
<!--                question_id: _question_id-->
<!--            }-->
<!--            fastapi('post', url, params,-->
<!--                (json) => {-->
<!--                    get_question()-->
<!--                },-->
<!--                (err_json) => {-->
<!--                    error = err_json-->
<!--                }-->
<!--            )-->
<!--        }-->
<!--    }-->

<!--    function vote_answer(answer_id) {-->
<!--        if(window.confirm('정말로 추천하시겠습니까?')) {-->
<!--            let url = "/apis/answers/vote/" + answer_id-->
<!--            let params = {-->
<!--                answer_id: answer_id-->
<!--            }-->
<!--            fastapi('post', url, params,-->
<!--                (json) => {-->
<!--                    get_question()-->
<!--                },-->
<!--                (err_json) => {-->
<!--                    error = err_json-->
<!--                }-->
<!--            )-->
<!--        }-->
<!--    }-->
<!--</script>-->


<!--<div class="container my-3">-->
<!--    &lt;!&ndash; 질문 &ndash;&gt;-->
<!--    <h2 class="border-bottom py-2">{question.subject}</h2>-->
<!--    <div class="card my-3">-->
<!--        <div class="card-body">-->
<!--            <div class="card-text" style="white-space: pre-line;">{question.content}</div>-->

<!--            <div class="d-flex justify-content-end">-->
<!--                {#if question.updated_at }-->
<!--                <div class="badge bg-light text-dark p-2 text-start mx-3">-->
<!--                    <div class="mb-2">수정일</div>-->
<!--                    <div>{moment.utc(question.updated_at).local().format("YYYY-MM-DD HH:mm")}</div>-->
<!--                </div>-->
<!--                {/if}-->
<!--                <div class="badge bg-light text-dark p-2">-->
<!--                    <div class="mb-2">{ question.author ? question.author.username : ""}</div>-->
<!--                    <div>{moment.utc(question.created_at).local().format('YYYY-MM-DD HH:mm')}</div>-->
<!--                </div>-->
<!--            </div>-->
<!--            <div class="my-3">-->
<!--                <button class="btn btn-sm btn-outline-secondary"-->
<!--                    on:click="{() => vote_question(question.id)}">-->
<!--                    추천-->
<!--                    <span class="badge rounded-pill bg-success">{ question.voter.length }</span>-->
<!--                </button>-->
<!--                {#if question.author && $username === question.author.username }-->
<!--                    <a use:link href="/question-update/{question.id}"-->
<!--                       class="btn btn-sm btn-outline-secondary">수정</a>-->
<!--                    <button class="btn btn-sm btn-outline-secondary"-->
<!--                            on:click={() => delete_question(question.id)}>삭제-->
<!--                    </button>-->
<!--                {/if}-->
<!--            </div>-->
<!--        </div>-->
<!--    </div>-->
<!--    <p class="text-end"><button class="btn btn-secondary" on:click="{() => {-->
<!--        push('/')-->
<!--    }}">목록으로</button></p>-->
<!--    &lt;!&ndash; 답변 목록 &ndash;&gt;-->
<!--    <h5 class="border-bottom my-3 py-2">{question.answers_all.length}개의 답변이 있습니다.</h5>-->
<!--    {#each question.answers_all as answer}-->
<!--    <div class="card my-3">-->
<!--        <div class="card-body">-->
<!--            <div class="card-text" style="white-space: pre-line;">{answer.content}</div>-->
<!--            <div class="d-flex justify-content-end">-->
<!--                {#if answer.updated_at }-->
<!--                <div class="badge bg-light text-dark p-2 text-start mx-3">-->
<!--                    <div class="mb-2">수정일</div>-->
<!--                    <div>{moment.utc(answer.updated_at).local().format('YYYY-MM-DD HH:mm')}</div>-->
<!--                </div>-->
<!--                {/if}-->
<!--                <div class="badge bg-light text-dark p-2">-->
<!--                    <div class="mb-2">{ answer.author ? answer.author.username : ""}</div>-->
<!--                    <div>{moment.utc(answer.created_at).local().format('YYYY-MM-DD HH:mm')}</div>-->
<!--                </div>-->
<!--            </div>-->
<!--            <div class="my-3">-->
<!--                <button class="btn btn-sm btn-outline-secondary"-->
<!--                    on:click="{() => vote_answer(answer.id)}">-->
<!--                    추천-->
<!--                    <span class="badge rounded-pill bg-success">{ answer.voter.length }</span>-->
<!--                </button>-->
<!--                {#if answer.author && $username === answer.author.username }-->
<!--                    <a use:link href="/answer-update/{answer.id}"-->
<!--                       class="btn btn-sm btn-outline-secondary">수정</a>-->
<!--                    <button class="btn btn-sm btn-outline-secondary"-->
<!--                            on:click={() => delete_answer(answer.id) }>삭제-->
<!--                    </button>-->
<!--                {/if}-->
<!--            </div>-->
<!--        </div>-->
<!--    </div>-->
<!--    {/each}-->
<!--    &lt;!&ndash; 답변 등록 &ndash;&gt;-->
<!--    <Error error={error} />-->
<!--    <form method="post" class="my-3">-->
<!--        <div class="mb-3">-->
<!--            <textarea rows="10" bind:value={content} disabled={$is_login ? "" : "disabled"} class="form-control"></textarea>-->
<!--        </div>-->
<!--        <p class="text-end"><input type="submit" value="답변등록" class="btn btn-primary {$is_login ? '' : 'disabled'}" on:click="{post_answer}" /></p>-->
<!--    </form>-->
<!--</div>-->


<script>
    import fastapi from "../lib/api"
    import Error from "../components/Error.svelte"
    import { link, push } from 'svelte-spa-router'
    import { is_login, username } from "../lib/store"
    import 'quill/dist/quill.snow.css'; // Quill 스노우 테마 CSS

    import moment from 'moment/min/moment-with-locales'
    moment.locale('ko')

    import DOMPurify from 'dompurify'

    export let params = {}
    let question_id = params.question_id
    /*Answer 모델에 Queston 모델을 연결할 때 backref="answers_all" 속성을 지정했기 때문*/
    let question = {answers_all:[], voter:[]}//, content: ''}
    let content = ""
    let error = {detail:[]}

    // DOMPurify config: video, source 태그와 관련 속성 허용
    const sanitizeConfig = {
        ADD_TAGS: ["video", "source"],
        ADD_ATTR: ["controls", "playsinline", "muted", "loop", "poster", "allowfullscreen", "src", "type", "width", "height", "style"]
    }

    function sanitizeQuestionAndAnswers(q) {
        // 안전하게 content 필드가 없을 때도 동작하도록 처리
        q.content_sanitized = DOMPurify.sanitize(q.content || "", sanitizeConfig)

        if (Array.isArray(q.answers_all)) {
            q.answers_all = q.answers_all.map(a => {
                // 복사하여 content_sanitized 필드 추가
                return {
                    ...a,
                    content_sanitized: DOMPurify.sanitize(a.content || "", sanitizeConfig)
                }
            })
        }
        return q
    }

    function get_question() {
        fastapi("get", "/apis/questions/detail/" + question_id, {}, (json) => {
            // 서버에서 온 raw 데이터를 로컬에서 정화(sanitize)해서 사용
            question = sanitizeQuestionAndAnswers(json)
        })
    }

    get_question()

    // quill 저장내용 quill.getText()


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

    function delete_question(_question_id) {
        if(window.confirm('정말로 삭제하시겠습니까?')) {
            let url = "/apis/questions/delete/" + _question_id
            let params = {
                question_id: _question_id
            }
            fastapi('delete', url, params,
                (json) => {
                    push('/')
                },
                (err_json) => {
                    error = err_json
                }
            )
        }
    }

    function delete_answer(answer_id) {
        if(window.confirm('정말로 삭제하시겠습니까?')) {
            let url = "/apis/answers/delete/" + answer_id
            let params = {
                answer_id: answer_id
            }
            fastapi('delete', url, params,
                (json) => {
                    get_question()
                },
                (err_json) => {
                    error = err_json
                }
            )
        }
    }

    function vote_question(_question_id) {
        if(window.confirm('정말로 추천하시겠습니까?')) {
            let url = "/apis/questions/vote/" + _question_id
            let params = {
                question_id: _question_id
            }
            fastapi('post', url, params,
                (json) => {
                    get_question()
                },
                (err_json) => {
                    error = err_json
                }
            )
        }
    }

    function vote_answer(answer_id) {
        if(window.confirm('정말로 추천하시겠습니까?')) {
            let url = "/apis/answers/vote/" + answer_id
            let params = {
                answer_id: answer_id
            }
            fastapi('post', url, params,
                (json) => {
                    get_question()
                },
                (err_json) => {
                    error = err_json
                }
            )
        }
    }
</script>


<style>
  :global(.post-container img) {
    max-width: 100%;
    height: auto;
    display: block;
  }
  :global(.post-container video) {
    max-width: 100%;
    height: auto;
    display: block;
  }

  :global(.ql-editor) {
       line-height: 1.8;
    }

   :global(.ql-code-block-container) {
       white-space: pre;
       background-color: #23241f;
       color: #f8f8f2;
       overflow: visible;
       margin-bottom: 5px;
       margin-top: 5px;
       padding: 10px 10px;
       border-radius: 6px;
   }
</style>

<div class="container my-3">
    <!-- 질문 -->
    <h2 class="border-bottom py-2">{question.subject}</h2>
    <div class="card my-3">
        <div class="card-body">
            <!-- sanitized HTML을 렌더링
            ql-editor class를 넣고,  import 'quill/dist/quill.snow.css';
            // Quill 스노우 테마 CSS을 넣으면, 에디터 형식이 유지된다.-->
            <div class="card-text post-container ql-editor">
                {@html question.content_sanitized || ""}
            </div>

            <div class="d-flex justify-content-end">
                {#if question.updated_at }
                <div class="badge bg-light text-dark p-2 text-start mx-3">
                    <div class="mb-2">수정일</div>
                    <div>{moment.utc(question.updated_at).local().format("YYYY-MM-DD HH:mm")}</div>
                </div>
                {/if}
                <div class="badge bg-light text-dark p-2">
                    <div class="mb-2">{ question.author ? question.author.username : ""}</div>
                    <div>{moment.utc(question.created_at).local().format('YYYY-MM-DD HH:mm')}</div>
                </div>
            </div>
            <div class="my-3">
                <button class="btn btn-sm btn-outline-secondary"
                    on:click="{() => vote_question(question.id)}">
                    추천
                    <span class="badge rounded-pill bg-success">{ question.voter.length }</span>
                </button>
                {#if question.author && $username === question.author.username }
                    <a use:link href="/question-update/{question.id}"
                       class="btn btn-sm btn-outline-secondary">수정</a>
                    <button class="btn btn-sm btn-outline-secondary"
                            on:click={() => delete_question(question.id)}>삭제
                    </button>
                {/if}
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
            <!-- 답변도 sanitized HTML로 렌더링 -->
            <div class="card-text post-container">
                {@html answer.content_sanitized || ""}
            </div>
            <div class="d-flex justify-content-end">
                {#if answer.updated_at }
                <div class="badge bg-light text-dark p-2 text-start mx-3">
                    <div class="mb-2">수정일</div>
                    <div>{moment.utc(answer.updated_at).local().format('YYYY-MM-DD HH:mm')}</div>
                </div>
                {/if}
                <div class="badge bg-light text-dark p-2">
                    <div class="mb-2">{ answer.author ? answer.author.username : ""}</div>
                    <div>{moment.utc(answer.created_at).local().format('YYYY-MM-DD HH:mm')}</div>
                </div>
            </div>
            <div class="my-3">
                <button class="btn btn-sm btn-outline-secondary"
                    on:click="{() => vote_answer(answer.id)}">
                    추천
                    <span class="badge rounded-pill bg-success">{ answer.voter.length }</span>
                </button>
                {#if answer.author && $username === answer.author.username }
                    <a use:link href="/answer-update/{answer.id}"
                       class="btn btn-sm btn-outline-secondary">수정</a>
                    <button class="btn btn-sm btn-outline-secondary"
                            on:click={() => delete_answer(answer.id) }>삭제
                    </button>
                {/if}
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
