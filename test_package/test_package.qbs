import qbs

Project {
	references: [ buildDirectory + '/../conanbuildinfo.qbs' ]
	Product {
		type: 'application'
		consoleApplication: true

		Depends { name: 'ConanBasicSetup' }

		Depends { name: 'cpp' }
		cpp.compilerPath: '/usr/local/bin/clang++'
		cpp.compilerPathByLanguage: {}
		cpp.cxxStandardLibrary: 'libstdc++'
		cpp.linkerPath: '/usr/local/bin/clang++'
		cpp.linkerWrapper: undefined
		cpp.minimumMacosVersion: '10.8'
		cpp.rpaths: [ buildDirectory + '/../../bin' ]
		cpp.target: 'x86_64-apple-macosx10.8'

		Depends { name: 'xcode' }
		xcode.sdk: 'macosx10.10'
		xcode.buildEnv.env.SDKROOT: undefined

		files: [ 'test_package.cc' ]
	}
}
