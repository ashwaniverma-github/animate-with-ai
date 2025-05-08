-- CreateTable
CREATE TABLE "Job" (
    "id" SERIAL NOT NULL,
    "prompt" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "storagePath" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completedAt" TIMESTAMP(3),

    CONSTRAINT "Job_pkey" PRIMARY KEY ("id")
);
