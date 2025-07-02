<template>
  <v-layout>
    <v-app-bar title="Wartezeiten in stuttgarter Bürgerbüros"></v-app-bar>

    <v-navigation-drawer width="340">
      <v-date-picker
        v-model="selectedDate"
        :min="minDate"
        :max="maxDate"
        :allowed-dates="allowedDates"
        first-day-of-week="1"
      ></v-date-picker>
    </v-navigation-drawer>

    <v-main>
      <v-container class="fill-height">
        <div>
          <div class="d-flex flex-wrap ga-md-4">
            <WaitingTimeChart
              v-for="office in offices"
              :key="office.id"
              :office="office"
              :selected-date="selectedDate.toDate()"
            />
          </div>
        </div>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, watchEffect } from "vue";
import { VDatePicker } from "vuetify/components";
import type { Office } from "@/ts/interfaces";
import { getOffices } from "@/ts/api";
import WaitingTimeChart from "./WaitingTimeChart.vue";
import dayjs, { Dayjs } from "dayjs";
import { toIsoDate } from "@/ts/utils";
import { useDate } from "vuetify";

const selectedDate = ref(dayjs());
const offices = ref<Office[]>([]);
const dateAdapter = useDate();

const minDate = ref("2025-06-26");

// today
const maxDate = ref(dateAdapter.format(new Date(), "YYYY-MM-DD"));

function allowedDates(date: unknown) {
  // Allow only weekdays
  const day = dayjs(date as Dayjs).day();
  return day !== 0 && day !== 6; // 0 = Sunday,
}

watchEffect(() => {
  console.log("Selected date todate changed:", selectedDate.value.toDate());
  console.log("Selected ISO date:", toIsoDate(selectedDate.value.toDate()));
});

onMounted(async () => {
  offices.value = await getOffices();
});
</script>
