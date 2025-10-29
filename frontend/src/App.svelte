<script>
    import Router from 'svelte-spa-router'
    import Home from "./routes/Home.svelte"
    import Detail from "./routes/Detail.svelte"
    import QuestionCreate from "./routes/QuestionCreate.svelte"

    const routes = {
        '/': Home,
        '/detail/:question_id': Detail,
        '/question-post': QuestionCreate,
    }
</script>

<Router {routes}/>