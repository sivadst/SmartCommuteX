"use client";

import { motion, type HTMLMotionProps } from "framer-motion";

export function MotionPanel(props: HTMLMotionProps<"section">) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      {...props}
    />
  );
}

