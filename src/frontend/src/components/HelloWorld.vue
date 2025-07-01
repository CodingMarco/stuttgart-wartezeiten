<template>
  <v-container class="fill-height" max-width="900">
    <div>
      <div class="mb-8 text-center">
        <h1 class="text-h2 font-weight-bold">
          Stuttgart Bürgerbüro Wartezeiten
        </h1>
      </div>

      <v-date-picker v-model="selectedDate"></v-date-picker>

      <div class="d-flex ga-md flex-wrap">
        {{ offices }}
      </div>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch, watchEffect, onMounted } from "vue";
import { VDatePicker } from "vuetify/components";
import { useDate } from "vuetify";

const dateAdapter = useDate();

const selectedDate = ref(new Date());

const offices = ref([]);

onMounted(async () => {
  // Fetch the office data from the API
  try {
    const response = await fetch("http://127.0.0.1:8000/offices");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    offices.value = await response.json();
  } catch (error) {
    console.error("Failed to fetch offices:", error);
  }
});

</script>
