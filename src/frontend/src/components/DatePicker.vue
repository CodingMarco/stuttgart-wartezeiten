<template>
  <v-date-picker
    v-model="internalDate"
    :min="minDate"
    :max="maxDate"
    :allowed-dates="allowedDates"
    first-day-of-week="1"
    v-bind="$attrs"
    @update:model-value="handleDateChange"
  ></v-date-picker>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import dayjs, { Dayjs } from "dayjs";
import { useDate } from "vuetify";

interface Props {
  modelValue: Dayjs;
}

interface Emits {
  (e: "update:modelValue", value: Dayjs): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const dateAdapter = useDate();
const internalDate = ref(props.modelValue);

const minDate = ref("2025-06-26");
const maxDate = ref(dateAdapter.format(new Date(), "YYYY-MM-DD"));

function allowedDates(date: unknown) {
  // Allow only weekdays
  const day = dayjs(date as Dayjs).day();
  return day !== 0 && day !== 6; // 0 = Sunday, 6 = Saturday
}

function handleDateChange(newDate: Dayjs) {
  emit("update:modelValue", newDate);
}

// Watch for external changes to modelValue
watch(
  () => props.modelValue,
  (newValue) => {
    internalDate.value = newValue;
  }
);
</script>
