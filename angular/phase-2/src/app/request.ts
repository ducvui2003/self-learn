export type Status = 'pending' | 'approved' | 'rejected';

// A leave request (休暇申請). Common screen in Japan enterprise apps.
export interface LeaveRequest {
  id: number;
  employeeEn: string;
  employeeJp: string;
  type: string; // leave type, e.g. Paid leave (有給休暇)
  days: number;
  status: Status;
  comment: string;
}

export const REQUESTS: LeaveRequest[] = [
  { id: 1, employeeEn: 'Taro Yamada', employeeJp: '山田 太郎', type: 'Paid leave (有給休暇)', days: 2, status: 'pending', comment: '' },
  { id: 2, employeeEn: 'Hanako Suzuki', employeeJp: '鈴木 花子', type: 'Sick leave (病気休暇)', days: 1, status: 'pending', comment: '' },
  { id: 3, employeeEn: 'Ichiro Tanaka', employeeJp: '田中 一郎', type: 'Paid leave (有給休暇)', days: 5, status: 'pending', comment: '' },
];
