<script>
  let count = $state(0)
  const increment = () => {
    count += 1
  }
</script>

<button type="button" class="btn btn-secondary" onclick={increment}>
  count is {count}
</button>
