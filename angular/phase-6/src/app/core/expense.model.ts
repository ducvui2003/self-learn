export type ExpenseStatus = 'pending' | 'approved' | 'rejected';
export type StatusFilter = 'all' | ExpenseStatus;

// Expense claim (経費精算) — common Japan enterprise workflow.
export interface Expense {
  id: number;
  employeeJp: string;
  employeeEn: string;
  category: string;
  amount: number; // yen
  status: ExpenseStatus;
}
