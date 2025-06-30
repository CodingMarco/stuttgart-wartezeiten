<template>
  <v-container class="fill-height" max-width="900">
    <div>
      <div class="mb-8 text-center">
        <h1 class="text-h2 font-weight-bold">
          Stuttgart Bürgerbüro Wartezeiten
        </h1>
      </div>

      <v-date-picker v-model="selectedDate"></v-date-picker>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { VDatePicker } from "vuetify/components";
import { useDate } from "vuetify";

const dateAdapter = useDate();

const selectedDate = ref(new Date());
</script>
