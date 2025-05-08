/*
  Warnings:

  - You are about to drop the `Job` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropTable
DROP TABLE "Job";

-- CreateTable
CREATE TABLE "job" (
    "id" SERIAL NOT NULL,
    "prompt" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "storage_path" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMP(3),

    CONSTRAINT "job_pkey" PRIMARY KEY ("id")
);
