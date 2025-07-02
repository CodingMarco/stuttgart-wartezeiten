export interface Office {
  label: string;
  url: string;
  id: number;
}

export interface StatusRecord {
  captured_at: string;
  status_id: number;
}

export interface Statuses {
  [id: string]: string;
}
