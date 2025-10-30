<script>
    import Router from 'svelte-spa-router'
    import Home from "./routes/Home.svelte"
    import Detail from "./routes/Detail.svelte"
    import QuestionCreate from "./routes/QuestionCreate.svelte"
    import UserRegister from "./routes/UserRegister.svelte"
    import UserLogin from "./routes/UserLogin.svelte"

    import Navigation from "./components/Navigation.svelte"

    const routes = {
        '/': Home,
        '/detail/:question_id': Detail,
        '/question-post': QuestionCreate,
        '/user-register': UserRegister,
        '/user-login': UserLogin,
    }
</script>

<Navigation />
<Router {routes}/>