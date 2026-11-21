plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlin.serialization)
}

android {
    sourceSets.getByName("main").assets.srcDir(rootProject.file("game-library/bank"))
    namespace = "com.example.triviaparty"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "com.example.triviaparty"
        minSdk = 24
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"

        val castReceiverId = providers.gradleProperty("castReceiverApplicationId").orElse("").get().trim()
        require(castReceiverId.isEmpty() || castReceiverId.matches(Regex("[0-9a-fA-F]{8}"))) {
            "castReceiverApplicationId must be the 8-character ID from the Google Cast Developer Console"
        }
        resValue("string", "cast_receiver_application_id", castReceiverId)

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    testOptions {
        unitTests.all {
            // QuestionBankRepository is a process-wide singleton that some tests reload while
            // others assume its original contents. One JVM per test class keeps results
            // independent of class order (adding a test class used to break unrelated tests).
            it.forkEvery = 1
        }
    }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    buildFeatures {
        compose = true
        resValues = true
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
            excludes += "META-INF/INDEX.LIST"
            excludes += "META-INF/io.netty.versions.properties"
        }
    }
}

dependencies {
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.graphics)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)

    // Serialization & Networking
    implementation(libs.kotlinx.serialization.json)
    implementation(libs.ktor.server.core)
    implementation(libs.ktor.server.cio)
    implementation(libs.ktor.server.websockets)
    implementation(libs.ktor.client.core)
    implementation(libs.ktor.client.cio)
    implementation(libs.ktor.client.websockets)

    // Image loading & Cast SDK
    implementation(libs.coil.compose)
    implementation(libs.play.services.cast.framework)
    implementation("com.google.zxing:core:3.5.3")

    testImplementation(libs.junit)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.compose.ui.test.junit4)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.junit)
    debugImplementation(libs.androidx.compose.ui.test.manifest)
    debugImplementation(libs.androidx.compose.ui.tooling)
}
