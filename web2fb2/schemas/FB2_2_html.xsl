<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:fb="http://www.gribuser.ru/xml/fictionbook/2.0">	<xsl:output method="html" encoding="UTF-8"/>	<xsl:param name="saveimages" select="2"/>	<xsl:param name="tocdepth" select="3"/>	<xsl:param name="toccut" select="1"/>	<xsl:param name="skipannotation" select="1"/>	<xsl:param name="NotesTitle" select="'Сноски'"/>	<xsl:include href="FB2_2_html_basics.xsl"/>	<xsl:key name="note-link" match="fb:section" use="@id"/>	<xsl:template match="/*">		<html>			<head>				<title>					<xsl:value-of select="fb:description/fb:title-info/fb:book-title"/>				</title>				<style type="text/css" media="screen">					<xsl:call-template name="CSS_Style_Screen"/>				</style>				<style type="text/css" media="print">					<xsl:call-template name="CSS_Style_Print"/>				</style>			</head>			<body>				<xsl:apply-templates select="fb:description/fb:title-info/fb:coverpage/fb:image"/>				<h1><xsl:apply-templates select="fb:description/fb:title-info/fb:book-title"/></h1>					<h2>					<small>						<xsl:for-each select="fb:description/fb:title-info/fb:author">								<b>									<xsl:call-template name="author"/>								</b>						</xsl:for-each>					</small>				</h2>				<xsl:if test="fb:description/fb:title-info/fb:sequence">					<p>						<xsl:for-each select="fb:description/fb:title-info/fb:sequence">							<xsl:call-template name="sequence"/><xsl:text disable-output-escaping="yes">&lt;br&gt;</xsl:text>						</xsl:for-each>					</p>				</xsl:if>				<xsl:if test="$skipannotation = 0">					<xsl:for-each select="fb:description/fb:title-info/fb:annotation">						<div>							<xsl:call-template name="annotation"/>						</div>						<hr/>					</xsl:for-each>				</xsl:if>				<!-- BUILD TOC -->				<xsl:if test="$tocdepth &gt; 0 and count(//fb:body[not(@name) or @name != 'notes']//fb:title) &gt; 1">					<hr/>					<blockquote>						<ul>							<xsl:apply-templates select="fb:body" mode="toc"/>						</ul>					</blockquote>				</xsl:if>				<!-- BUILD BOOK -->				<xsl:call-template name="DocGen"/>			</body>		</html>	</xsl:template></xsl:stylesheet><!-- Stylus Studio meta-information - (c) 2004-2008. Progress Software Corporation. All rights reserved.
<metaInformation>
	<scenarios>
		<scenario default="no" name="Scenario1" userelativepaths="yes" externalpreview="no" url="in__.fb2" htmlbaseurl="" outputurl="" processortype="saxon8" useresolver="yes" profilemode="0" profiledepth="" profilelength="" urlprofilexml="" commandline=""
		          additionalpath="" additionalclasspath="" postprocessortype="none" postprocesscommandline="" postprocessadditionalpath="" postprocessgeneratedext="" validateoutput="no" validator="internal" customvalidator="">
			<advancedProp name="sInitialMode" value=""/>
			<advancedProp name="bXsltOneIsOkay" value="true"/>
			<advancedProp name="bSchemaAware" value="true"/>
			<advancedProp name="bXml11" value="false"/>
			<advancedProp name="iValidation" value="0"/>
			<advancedProp name="bExtensions" value="true"/>
			<advancedProp name="iWhitespace" value="0"/>
			<advancedProp name="sInitialTemplate" value=""/>
			<advancedProp name="bTinyTree" value="true"/>
			<advancedProp name="bWarnings" value="true"/>
			<advancedProp name="bUseDTD" value="false"/>
			<advancedProp name="iErrorHandling" value="fatal"/>
		</scenario>
		<scenario default="no" name="Scenario2" userelativepaths="yes" externalpreview="no" url="v.fb2" htmlbaseurl="" outputurl="" processortype="saxon8" useresolver="yes" profilemode="0" profiledepth="" profilelength="" urlprofilexml="" commandline=""
		          additionalpath="" additionalclasspath="" postprocessortype="none" postprocesscommandline="" postprocessadditionalpath="" postprocessgeneratedext="" validateoutput="no" validator="internal" customvalidator="">
			<advancedProp name="sInitialMode" value=""/>
			<advancedProp name="bXsltOneIsOkay" value="true"/>
			<advancedProp name="bSchemaAware" value="true"/>
			<advancedProp name="bXml11" value="false"/>
			<advancedProp name="iValidation" value="0"/>
			<advancedProp name="bExtensions" value="true"/>
			<advancedProp name="iWhitespace" value="0"/>
			<advancedProp name="sInitialTemplate" value=""/>
			<advancedProp name="bTinyTree" value="true"/>
			<advancedProp name="bWarnings" value="true"/>
			<advancedProp name="bUseDTD" value="false"/>
			<advancedProp name="iErrorHandling" value="fatal"/>
		</scenario>
		<scenario default="yes" name="Scenario3" userelativepaths="yes" externalpreview="no" url="in__.fb2" htmlbaseurl="" outputurl="" processortype="saxon8" useresolver="yes" profilemode="0" profiledepth="" profilelength="" urlprofilexml=""
		          commandline="" additionalpath="" additionalclasspath="" postprocessortype="none" postprocesscommandline="" postprocessadditionalpath="" postprocessgeneratedext="" validateoutput="no" validator="internal" customvalidator="">
			<advancedProp name="sInitialMode" value=""/>
			<advancedProp name="bXsltOneIsOkay" value="true"/>
			<advancedProp name="bSchemaAware" value="true"/>
			<advancedProp name="bXml11" value="false"/>
			<advancedProp name="iValidation" value="0"/>
			<advancedProp name="bExtensions" value="true"/>
			<advancedProp name="iWhitespace" value="0"/>
			<advancedProp name="sInitialTemplate" value=""/>
			<advancedProp name="bTinyTree" value="true"/>
			<advancedProp name="bWarnings" value="true"/>
			<advancedProp name="bUseDTD" value="false"/>
			<advancedProp name="iErrorHandling" value="fatal"/>
		</scenario>
	</scenarios>
	<MapperMetaTag>
		<MapperInfo srcSchemaPathIsRelative="yes" srcSchemaInterpretAsXML="no" destSchemaPath="" destSchemaRoot="" destSchemaPathIsRelative="yes" destSchemaInterpretAsXML="no"/>
		<MapperBlockPosition></MapperBlockPosition>
		<TemplateContext></TemplateContext>
		<MapperFilter side="source"></MapperFilter>
	</MapperMetaTag>
</metaInformation>-->