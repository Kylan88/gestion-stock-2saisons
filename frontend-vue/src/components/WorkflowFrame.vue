<template>
  <section class="workflow-frame" :style="{ '--step': step }">
    <div class="workflow-frame-copy">
      <span class="workflow-frame-kicker">Flux {{ String(step).padStart(2, '0') }} · {{ eyebrow }}</span>
      <h2>{{ title }}</h2>
      <p>{{ description }}</p>
    </div>

    <div class="workflow-tracker" aria-label="Progression du flux de production">
      <template v-for="(item, index) in stages" :key="item.short">
        <span class="workflow-tracker-step" :class="{ done: index + 1 < step, active: index + 1 === step }">
          <b>{{ index + 1 }}</b><em>{{ item.short }}</em>
        </span>
        <span v-if="index < stages.length - 1" class="workflow-tracker-line" :class="{ done: index + 1 < step }"></span>
      </template>
    </div>

    <div v-if="$slots.meta" class="workflow-frame-meta"><slot name="meta" /></div>
  </section>
</template>

<script setup>
defineProps({
  step: { type: Number, required: true },
  eyebrow: { type: String, required: true },
  title: { type: String, required: true },
  description: { type: String, required: true },
})

const stages = [
  { short: 'Réception' },
  { short: 'Tri' },
  { short: 'Séchage' },
  { short: 'Condition.' },
  { short: 'Stock' },
]
</script>

<style scoped>
.workflow-frame {
  display: grid; grid-template-columns: minmax(230px, 1.2fr) minmax(370px, 1fr) auto; align-items: center; gap: 24px;
  margin: 0 0 24px; padding: 20px 24px; border: 1px solid #e5e7eb; border-radius: 12px;
  background: white; box-shadow: 0 1px 3px rgb(0 0 0 / 0.1);
}
.workflow-frame-kicker { display: block; color: #00853E; font-size: 10px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
.workflow-frame h2 { margin: 4px 0 6px; font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 700; color: #111827; }
.workflow-frame p { max-width: 430px; color: #6b7280; font-size: 13px; line-height: 1.5; }
.workflow-tracker { display: flex; align-items: flex-start; justify-content: center; }
.workflow-tracker-step { display: flex; flex-direction: column; align-items: center; gap: 5px; min-width: 40px; color: #9ca3af; }
.workflow-tracker-step b { width: 28px; height: 28px; display: grid; place-items: center; border: 1px solid #e5e7eb; border-radius: 50%; background: white; font-size: 11px; font-weight: 700; }
.workflow-tracker-step em { font-style: normal; font-size: 10px; font-weight: 600; white-space: nowrap; }
.workflow-tracker-step.done, .workflow-tracker-step.active { color: #00853E; }
.workflow-tracker-step.done b { background: #00853E; color: white; border-color: #00853E; }
.workflow-tracker-step.active b { background: #dcfce7; color: #00853E; border-color: #86efac; box-shadow: 0 0 0 4px rgba(220,252,231,0.5); }
.workflow-tracker-line { width: clamp(15px, 3.4vw, 44px); height: 2px; margin-top: 13px; background: #e5e7eb; border-radius: 1px; }
.workflow-tracker-line.done { background: #00853E; }
.workflow-frame-meta { min-width: 112px; padding: 12px 16px; border-radius: 12px; background: #f9fafb; border: 1px solid #e5e7eb; color: #111827; }
@media (max-width: 1100px) { .workflow-frame { grid-template-columns: 1fr auto; } .workflow-tracker { grid-column: 1 / -1; grid-row: 2; justify-content: flex-start; } }
@media (max-width: 640px) { .workflow-frame { display: block; padding: 18px; } .workflow-tracker { margin-top: 18px; overflow-x: auto; justify-content: flex-start; } .workflow-frame-meta { display: inline-block; margin-top: 12px; } }
</style>
