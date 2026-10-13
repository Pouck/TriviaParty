package com.example.triviaparty.data

import java.io.File
import java.io.InputStream

/** Installs original sets once as ordinary editable packages. Deletions survive restarts. */
object OriginalPackageMigration {
    fun seed(packagesDirectory: File, archives: List<Pair<String, () -> InputStream>>) {
        packagesDirectory.mkdirs()
        val marker = File(packagesDirectory, ".original-sets-v1")
        if (marker.isFile) return
        archives.forEach { (id, open) ->
            if (!File(packagesDirectory, id).isDirectory) {
                val imported = GamePackageImportRepository.importArchive(open(), packagesDirectory, id)
                GamePackageImportRepository.confirmImport(imported)
            }
        }
        marker.writeText("installed\n")
    }
}
