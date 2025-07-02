<template>
  <v-layout>
    <v-app-bar title="Wartezeiten in stuttgarter Bürgerbüros"></v-app-bar>

    <!-- Desktop: Navigation drawer -->
    <v-navigation-drawer width="340" class="d-none d-md-flex">
      <DatePicker v-model="selectedDate" />
    </v-navigation-drawer>

    <v-main>
      <v-container class="fill-height">
        <!-- Mobile: Date picker above charts -->
        <v-row class="d-flex d-md-none mb-4">
          <v-col cols="12">
            <v-card>
              <v-card-title class="text-h6">Select Date</v-card-title>
              <v-card-text>
                <DatePicker v-model="selectedDate" width="100%" hide-header />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Charts -->
        <v-row>
          <v-col v-for="office in offices" :key="office.id" cols="12" md="6">
            <WaitingTimeChart
              :office="office"
              :selected-date="selectedDate.toDate()"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup lang="ts">
import { ref, onMounted, watchEffect } from "vue";
import type { Office } from "@/ts/interfaces";
import { getOffices } from "@/ts/api";
import WaitingTimeChart from "./WaitingTimeChart.vue";
import DatePicker from "./DatePicker.vue";
import dayjs from "dayjs";
import { toIsoDate } from "@/ts/utils";

const selectedDate = ref(dayjs());
const offices = ref<Office[]>([]);

watchEffect(() => {
  console.log("Selected date todate changed:", selectedDate.value.toDate());
  console.log("Selected ISO date:", toIsoDate(selectedDate.value.toDate()));
});

onMounted(async () => {
  offices.value = await getOffices();
});
</script>
