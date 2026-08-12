<script setup lang="ts">
  defineProps<{
    size: string
    backgroundColor: string
  }>()
</script>

<template>
  <div class="spinner" :style="{ width: size, height: size }">
    <div class="double-bounce1" :style="{ backgroundColor: backgroundColor }"></div>
    <div class="double-bounce2" :style="{ backgroundColor: backgroundColor }"></div>
  </div>
</template>

<style scoped>
  .spinner {
    position: relative;
    margin: 100px auto;
  }

  .double-bounce1,
  .double-bounce2 {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    opacity: 0.6;
    position: absolute;
    top: 0;
    left: 0;

    animation: sk-bounce 2s infinite ease-in-out;
  }

  .double-bounce2 {
    animation-delay: -1s;
  }

  @keyframes sk-bounce {
    0%,
    100% {
      transform: scale(0);
    }
    50% {
      transform: scale(1);
    }
  }
</style>
