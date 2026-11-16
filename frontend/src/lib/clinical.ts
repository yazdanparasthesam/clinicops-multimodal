export function bmiCategory(bmi:number): string {
  if (bmi < 18.5) return "Underweight"
  if (bmi < 25) return "Normal"
  if (bmi < 30) return "Overweight"
  return "Obese"
}
export function deadlineCountdown(deadline:string): string {
  const diff = new Date(deadline).getTime() - Date.now()
  const h = Math.floor(diff/3600000)
  if (h<0) return "OVERDUE"
  return `${h}h left`
}
export function validationBadge(severity:string): string {
  return severity==="error" ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"
}
